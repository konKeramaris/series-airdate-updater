import boto3
import os
from requests import get
from tabulate import tabulate
from datetime import datetime
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client              = boto3.client('ses')
SERIES_NAMES_SSM    = os.environ['NAMES_SSM_NAME']
SERIES_IDS_SSM      = os.environ['IDS_SSM_NAME']
SRC_EMAIL           = os.environ['SRC_EMAIL']
DST_EMAIL           = os.environ['SRC_EMAIL']
BASE_URL            = os.environ['BASE_URL']

ssmclient   = boto3.client('ssm')
series      = ssmclient.get_parameter(Name=SERIES_NAMES_SSM)['Parameter']['Value'].split(',')
ids         = ssmclient.get_parameter(Name=SERIES_IDS_SSM)['Parameter']['Value'].split(',')

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

def findLatestPreviousEpisode(response):
    # Find the latest airdate that is not empty and previous that the current day
    latestPreviousPointer = -1
    while (response[latestPreviousPointer]['airdate'] > CURRENT_DATE) or (response[latestPreviousPointer]['airdate'] == ''): 
        latestPreviousPointer -=1
    logger.info('pointer %s' %latestPreviousPointer)

    # response[latestPreviousPointer] is the previous episode
    # response[latestPreviousPointer+1] is the next episode (if it exists)
    # if latestPreviousPointer is -1 then it means that there is no data for any future episodes
    return latestPreviousPointer

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
    logger.info('id: %s' %id)

    # Return a sorted json with all the episodes of the tv series
    response = get(BASE_URL+'/shows/'+id+'/episodes').json()
    logger.info('%s' %response)

    latestPreviousPointer = findLatestPreviousEpisode(response)

    prevEp.append(getEpisodesFromEpisodeList(response, latestPreviousPointer))
    nextEp.append(getEpisodesFromEpisodeList(response, latestPreviousPointer+1))
    prevDates.append(getDatesFromEpisodeList(response, latestPreviousPointer))
    nextDates.append(getDatesFromEpisodeList(response, latestPreviousPointer+1))

# Sort, Combine and Transpose List
nextDates, series, nextEp, prevDates, prevEp = zip(*sorted(zip(nextDates, series, nextEp, prevDates, prevEp)))
transposedList = list(map(list, zip(*[series, prevEp, prevDates, nextEp, nextDates])))

def lambda_handler(event, context):
    data = tabulate(transposedList, headers=['Name', 'Prev. Ep.','Airtime','Next Ep.','Airtime'], 
                                    colalign=("left","center","left","center","center"), tablefmt="html")
    response = sendSESEmail(data)
    return response