# Series Airdate Updater

This Solution utilizes the open TVmaze API to provide weekly email updates on the airdates of your ongoing tv series. 

## Architecture
The Solution is based around the AWS Lambda functions that invokes the API and retrieves the latest information about the series airdates. The function then uses the Amazon SES service to send an update email. Cloudwatch Events is used to schedule the triggering of the Lambda function. Lastly the update of the list of series is handled by a python script located in `update-series-list/`.

![architecture](imgs/architecture.png)

# Todo
* Add logging on Lambda
* Verify Cloudwatch events
* Verify free-tier
* Resolve "The-Boys" issue
* Improve README
* Investigate Integration with Calendar

## Prerequisites
* AWS Account
* Install and configure `aws-cli` and `sam-cli`
* Working `python3.7` environment
* Set up email on Amazon SES (Cannot be done via Cloudformation)
  * [Amazon SES Quick Start](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/quick-start.html)
  * [Setting up Email with Amazon SES](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-email-set-up.html)

## How to deploy (SAM)
#### Connect to python3.7 virtual Environment
``` bash
# source ~/Documents/python/python37/bin/activate
p37
```
#### Install Dependencies
``` bash
sam build
```

#### Deploy the Infrastructure & Code
``` bash
sam deploy --stack-name airdate --s3-bucket kostas-test-bucket-eu-west-1 --region eu-west-1 --capabilities CAPABILITY_NAMED_IAM --parameter-overrides Email=email@example.com
```

#### Update Series List
``` bash
python3 update-series-list/update-series-list.py -l airdate-update-function
```


## How to deploy (Cloudformation)
#### Install Dependencies
``` bash
cd lambda
pip3 install --target ./package requests tabulate datetime --system
```
#### Deploy Code on existing Function
``` bash
cd package/ && zip -r9 function.zip . && cd .. && zip -g function.zip lambda_function.py && aws lambda update-function-code --function-name test-airtime --zip-file fileb://function.zip
```