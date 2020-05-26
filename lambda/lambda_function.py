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

CURRENT_DATE = str(datetime.now().date())
EMAIL_SUBJECT = 'Your Weekly Series Airtime Updater'

def sendSESEmail(data):
    response = client.send_email(Source=SRC_EMAIL,Destination={'ToAddresses': [DST_EMAIL],},
                                Message={
                                    'Body': {
                                        'Html': {
                                            'Charset': 'UTF-8', 
                                            'Data': data,
                                            }
                                        },
                                    'Subject': { 
                                        'Charset': 'UTF-8', 
                                        'Data': EMAIL_SUBJECT
                                        }
                                    })
    return response['ResponseMetadata']['HTTPStatusCode']

def getDatesFromEpisodeList(data, index):
    if index == 0 or data[index]['airdate']=='':
        return 'N/A'
    else:
        return data[index]['airdate']

def getEpisodesFromEpisodeList(data, index):
    if index == 0:
        return 'N/A'
    else:
        return 's'+str(data[index]['season'])+'e'+str(data[index]['number'])

nextDates = []; nextEp = []; prevDates = []; prevEp = []
for id in ids:
    response = get(BASE_URL+'/shows/'+id+'/episodes').json()
    pointer = -1
    # Find the latest airdate that is not empty and previous that the current day
    while (response[pointer]['airdate'] > CURRENT_DATE) or (response[pointer]['airdate'] == ''): pointer -=1
    # response[pointer] is the previous episode
    # response[pointer+1] is the next episode (if it exists)
    prevEp.append(getEpisodesFromEpisodeList(response, pointer))
    nextEp.append(getEpisodesFromEpisodeList(response, pointer+1))
    prevDates.append(getDatesFromEpisodeList(response, pointer))
    nextDates.append(getDatesFromEpisodeList(response, pointer+1))

# Sort, Combine and Transpose List
nextDates, series, nextEp, prevDates, prevEp = zip(*sorted(zip(nextDates, series, nextEp, prevDates, prevEp)))
transposedList = list(map(list, zip(*[series, prevEp, prevDates, nextEp, nextDates])))

def lambda_handler(event, context):
    data = tabulate(transposedList, headers=['Name', 'Prev. Ep.','Airtime','Next Ep.','Airtime'], 
                                    colalign=("left","center","left","center","center"), tablefmt="html")
    response = sendSESEmail(data)
    return response