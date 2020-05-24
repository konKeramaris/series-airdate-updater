import json
import boto3
import os
from requests import get
from tabulate import tabulate
from datetime import datetime

client = boto3.client('ses')
series      = os.environ['SERIES_LIST'].split(',')
ids         = os.environ['IDS_LIST'].split(',')
SRC_EMAIL   = os.environ['SRC_EMAIL']
DST_EMAIL   = os.environ['SRC_EMAIL']
BASE_URL    = os.environ['BASE_URL']

nextDates = []; nextEp = []; prevDates = []; prevEp=[]
for i in ids:
    response = get(BASE_URL+'/shows/'+i+'/episodes')
    if response.json()[-1]['airdate'] > str(datetime.now().date()):
        # If episode is later than the current day
        # then show the last previous episode and the upcoming episode
        prevEp.append('s'+str(response.json()[-2]['season'])+'e'+str(response.json()[-2]['number']))
        prevDates.append(response.json()[-2]['airdate'])
        nextEp.append('s'+str(response.json()[-1]['season'])+'e'+str(response.json()[-1]['number']))
        nextDates.append(response.json()[-1]['airdate'])
    else:
        prevEp.append('s'+str(response.json()[-1]['season'])+'e'+str(response.json()[-1]['number']))
        prevDates.append(response.json()[-1]['airdate'])
        nextDates.append('No Data')
        nextEp.append('No Data')

# Sort, Combine and Transpose List
nextDates, series, nextEp, prevDates, prevEp = zip(*sorted(zip(nextDates, series, nextEp, prevDates, prevEp)))
transposedList = list(map(list, zip(*[series, prevEp, prevDates, nextEp, nextDates])))

def lambda_handler(event, context):    
    response = client.send_email(
        Destination={'ToAddresses': [DST_EMAIL],},
        Message={
            'Body': {'Html': {'Charset': 'UTF-8', 'Data': tabulate(transposedList, headers=['Name', 'Previous Ep.','Airtime','Next Ep.','Airtime'], tablefmt="html"),}},
            'Subject': { 'Charset': 'UTF-8', 'Data': 'Your Weekly Series Airtime Updater',},
        },
        Source=SRC_EMAIL)
    return response['ResponseMetadata']['HTTPStatusCode']