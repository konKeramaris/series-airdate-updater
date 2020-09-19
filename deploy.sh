#! /bin/bash
while getopts e:s:d:p:r option
  do
  case "${option}" in
    r) REMOVE=true;;
    e) ENVIRONMENT=${OPTARG};;
    s) SRC_EMAIL=${OPTARG};;
    d) DST_EMAIL=${OPTARG};;
    p) PROJECT_NAME=${OPTARG};;
  esac
done

export S3_BUCKET_NAME=$PROJECT_NAME-$ENVIRONMENT-artifacts-s3

export INIT_STACK_NAME=$PROJECT_NAME-$ENVIRONMENT-init
export NOTIFICATION_LAMBDA_STACK_NAME=$PROJECT_NAME-$ENVIRONMENT-notification-lambda
export SERIES_AIRDATE_UPDATER_LAMBDA_STACK_NAME=$PROJECT_NAME-$ENVIRONMENT-lambda


if [ "$REMOVE" = true ] ; then
  echo 'Removing Cloudformation'
  aws s3 rm s3://$S3_BUCKET_NAME/ --recursive
  aws cloudformation delete-stack --stack-name $INIT_STACK_NAME
  aws cloudformation delete-stack --stack-name $SERIES_AIRDATE_UPDATER_LAMBDA_STACK_NAME
  aws cloudformation delete-stack --stack-name $NOTIFICATION_LAMBDA_STACK_NAME
else
  echo 'Creating Initial Cloudformation'    
  aws cloudformation deploy --template-file init-cloudformation.yaml --stack-name $INIT_STACK_NAME --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT BucketName=$S3_BUCKET_NAME --no-fail-on-empty-changeset

  cd notification-lambda
  pipreqs src/ --force
  mkdir package
  sed -i '/boto3/d' src/requirements.txt
  pip3 install --target package/ -r src/requirements.txt
  cp src/. package/ -a

  aws cloudformation package --template-file lambda.yaml --s3-bucket $S3_BUCKET_NAME --output-template-file packaged-lambda.yaml

  aws cloudformation deploy --template-file packaged-lambda.yaml --stack-name $NOTIFICATION_LAMBDA_STACK_NAME --capabilities CAPABILITY_NAMED_IAM --parameter-overrides ProjectName=$PROJECT_NAME SrcEmail=$SRC_EMAIL DstEmail=$DST_EMAIL Environment=$ENVIRONMENT
  rm packaged-lambda.yaml
  rm package/ -r

  export NOTIFICATION_LAMBDA_ARN=`aws cloudformation describe-stacks --stack-name $NOTIFICATION_LAMBDA_STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='LambdaArn'].OutputValue" --output text`
  echo $NOTIFICATION_LAMBDA_ARN
  
  cd ../weekly-updater-lambda

  echo 'Deploy Series Airdate Updater lambda'
  sam build 
  sam deploy --stack-name $SERIES_AIRDATE_UPDATER_LAMBDA_STACK_NAME --s3-bucket $S3_BUCKET_NAME --region eu-west-1 --capabilities CAPABILITY_NAMED_IAM --parameter-overrides SrcEmail=$SRC_EMAIL DstEmail=$DST_EMAIL ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT NotificationLambdaArn=$NOTIFICATION_LAMBDA_ARN

  python ../update-series-list/update-series-list.py -e dev -p $PROJECT_NAME
fi