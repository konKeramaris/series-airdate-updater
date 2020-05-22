# Series Airtime Updater

# Todo
* Cloudformation for Cloudwatch Events
* Ability to retrieve existing series list from Lambda Environment Variables on update-series-list.py
* Investigate Integration with Calendar

## How to deploy (SAM)
#### Connect to python3.7 virtual Environment
```
# source ~/Documents/python/python37/bin/activate
p37
```
#### Install Dependencies
`sam build`


#### Deploy the Infrastructure & Code
`sam deploy --stack-name airdate --s3-bucket kostas-test-bucket-eu-west-1 --region eu-west-1 --capabilities CAPABILITY_NAMED_IAM --parameter-overrides Email=email@example.com`

#### Update Series List
`python3 update-series-list/update-series-list.py -l airdate-update-function`


## How to deploy (Cloudformation)
#### Install Dependencies
```
cd lambda
pip3 install --target ./package requests tabulate datetime --system
```
#### Deploy Code on existing Function
`cd package/ && zip -r9 function.zip . && cd .. && zip -g function.zip lambda_function.py && aws lambda update-function-code --function-name test-airtime --zip-file fileb://function.zip`