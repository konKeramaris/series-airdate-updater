# Series Airdate Updater

This Solution utilizes the open  [TVmaze](https://www.tvmaze.com/) API to provide weekly email updates and notifications on the air-dates of your ongoing TV series. It operates 100% within the free-tier of AWS and will lead to no extra costs.

# Architecture
The Solution is based around 2 AWS Lambda functions:

**Weekly Updater Function**

This Function is triggered on a weekly bases by an Events Rule., it invokes the TVmaze API and retrieves the latest information about the series air-dates. The function then uses the Amazon SES service to send an update email. The update of the list of series is handled by a python script located in `update-series-list/`. When this function Identifies a new announced episode it will create an events rule on the day of the aired episode with the correct information to trigger the Notification Lambda

**Notification Function**

This Function is triggered on the day of a new aired episode and sends an SES notification to the user. 



![architecture](imgs/architecture.svg)

The Solution sends you an email with information similar to the following table:

| Name           | Previous Ep. | Airtime    | Next Ep. | Airtime    |
| -------------- | ------------ | ---------- | -------- | ---------- |
| 13 Reasons Why | s3e13        | 2019-08-23 | s4e1     | 2020-06-05 |
| The Boys       | s1e8         | 2019-07-26 | s2e1     | 2020-09-04 |
| Atlanta        | s2e11        | 2018-05-10 | N/A      | N/A        |
| Westworld      | s3e8         | 2020-05-03 | N/A      | N/A        |

# Prerequisites
* AWS Account
* Install and configure `aws-cli` and `sam-cli`
* Working `python3.7` environment (required for `sam-cli`)
* Set up email on Amazon SES (Cannot be done via CloudFormation)
  * [Amazon SES Quick Start](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/quick-start.html)
  * [Setting up Email with Amazon SES](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-email-set-up.html)
* Create a `myseries.txt` file in the `update-series-list/` directory and add your TV Series (one Series per line) 

# How to deploy
To deploy the Infrastructure you can use the `deploy.sh` shell script and provide the following arguments:

| Name | Description                                                  |
| ---- | ------------------------------------------------------------ |
| `-p` | Project Name: A Name String (Project Name) that all your resources will receive (e.g. my-series-update) |
| `-e` | Environment: The Environment that you will deploy to (e.g. prod) |
| `-s` | Src Email: The source email address (e.g. src@example.com). Needs to be already configured on SES. |
| `-d` | Dst Email: The destination email address (e.g. dst@example.com). Needs to be already configured on SES. |
| `-r` | Remove: Add `-r` only when you want to completely remove all the infrastructure |

The command to deploy will look like:

```bash
./deploy.sh -p "my-series-update" -e "prod" -s "src@example.com" -d "dst@example.com" 
```

To completely remove all the infrastructure you can do:

```bash
./deploy.sh -p "my-series-update" -e "prod" -s "src@example.com" -d "dst@example.com" -r
```


### Update Series List
You can interact (update/retrieve) with the SSM Parameter of your TV Series list by using the  `update-series-list.py`  script.

First install the necessary requirements:

``` bash
pip3 install -r update-series-list/requirements.txt
```

Then, you can update the SSM Parameters by providing the appropriate input parameters.
``` bash
python3 update-series-list/update-series-list.py --filename <txt-file-name>
```
where `<txt-file-name>` is a text file that has written your series titles (one per line). This script will read the list of TV series from `<txt-file-name>`  retrieve their ids and then update the SSM Parameters with the appropriate values. You can run again this script if you want to add/remove more series.

You can also retrieve the current Lambda series list and save it on a file by doing:
``` bash
python3 update-series-list/update-series-list.py --getserieslist --filename <txt-file-name>
```


# License
Licensed under the Apache License, Version 2.0 ([LICENSE](LICENSE)
or http://www.apache.org/licenses/LICENSE-2.0).

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall be
licensed as above, without any additional terms or conditions.
