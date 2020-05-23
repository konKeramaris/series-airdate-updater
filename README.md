# Series Airdate Updater

# Todo
* Cloudformation for Cloudwatch Events
* Ability to retrieve existing series list from Lambda Environment Variables on update-series-list.py
* Investigate Integration with Calendar

## Prerequisites
* Install and configure `aws-cli` and `sam-cli`
* Working `python3.7` environment
* Set up email on Amazon SES

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