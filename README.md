# Series Airdate Updater

This Solution utilizes the open TVmaze API to provide weekly email updates on the air-dates of your ongoing TV series. 

## Architecture
The Solution is based around the AWS Lambda functions that invokes the API and retrieves the latest information about the series air-dates. The function then uses the Amazon SES service to send an update email. CloudWatch Events is used to schedule the triggering of the Lambda function. Lastly the update of the list of series is handled by a python script located in `update-series-list/`.

![architecture](imgs/architecture.png)

# Todo
* Add logging on Lambda
* Verify CloudWatch events
* Verify free-tier
* Resolve "The-Boys" issue
* Improve README
* Investigate Integration with Calendar

## Prerequisites
* AWS Account
* Install and configure `aws-cli` and `sam-cli`
* Working `python3.7` environment
* Set up email on Amazon SES (Cannot be done via CloudFormation)
  * [Amazon SES Quick Start](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/quick-start.html)
  * [Setting up Email with Amazon SES](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-email-set-up.html)

## How to deploy (SAM)
#### Install Dependencies
``` bash
sam build
```

#### Deploy the Infrastructure & Code
``` bash
sam deploy --stack-name airdate --s3-bucket kostas-test-bucket-eu-west-1 --region eu-west-1 --capabilities CAPABILITY_NAMED_IAM --parameter-overrides Email=email@example.com
```

#### Update Series List
First install the necessary requirements for the `update-series-list.py` script by doing:
``` bash
pip3 install -r update-series-list/requirements.txt
```

Then, you can update the Lambda Environment variables by providing the appropriate input parameters.
``` bash
python3 update-series-list/update-series-list.py --lambdaname <function-name> --filename <txt-file-name>
```
where `<txt-file-name>` is a text file that has your series titles (one per line). This script will read the list of TV series from `<txt-file-name>`  retrieve their ids and then update the Lambda Environment variables with the appropriate values. You can run again this script if you want to add/remove more series.



You can also retrieve the current Lambda series list and save it on a file by doing:

``` bash
python3 update-series-list/update-series-list.py --getserieslist --filename <txt-file-name>
```

**Note:** When redeploying, depending on the changes of the Lambda function in AWS, you might need to run again `update-series-list/update-series-list.py` to set the series list in the Lambda Environment Variables.