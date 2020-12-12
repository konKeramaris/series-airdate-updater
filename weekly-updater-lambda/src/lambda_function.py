import boto3
import os
from requests import get
from tabulate import tabulate
from datetime import datetime
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client                  = boto3.client('ses')
SERIES_SSM              = os.environ['SERIES_SSM']
SRC_EMAIL               = os.environ['SRC_EMAIL']
DST_EMAIL               = os.environ['DST_EMAIL']
BASE_URL                = os.environ['BASE_URL']
NOTIFICATION_LAMBDA_ARN = os.environ['NOTIFICATION_LAMBDA_ARN']
ENVIRONMENT             = os.environ['ENVIRONMENT']
PROJECT_NAME            = os.environ['PROJECT_NAME']
# For debugging purposes you have the ability to set a custom cron job to test the invocation of the notification function
CUSTOM_CRON_JOB         = os.environ['CUSTOM_CRON_JOB']

ssmclient   = boto3.client('ssm')
eventClient = boto3.client('events')
series      = json.loads(ssmclient.get_parameter(Name=SERIES_SSM)['Parameter']['Value'])

CURRENT_DATE = str(datetime.now().date())
EMAIL_SUBJECT = 'Your Weekly Series Airdate Updater'

def sendSESEmail(data):
    response = client.send_email(Source=SRC_EMAIL,Destination={'ToAddresses': [DST_EMAIL],},
                                Message={
                                    'Body': {
                                        'Html': {'Charset': 'UTF-8', 'Data': data,}
                                        },
                                    'Subject': { 'Charset': 'UTF-8', 'Data': EMAIL_SUBJECT}
                                    })
    return response['ResponseMetadata']['HTTPStatusCode']

def findlatestAiredEpisode(response):
    # Find the latest airdate that is not empty and previous that the current day
    latestAiredPointer = -1
    while (response[latestAiredPointer]['airdate'] > CURRENT_DATE) or (response[latestAiredPointer]['airdate'] == ''): 
        latestAiredPointer -=1
    logger.info('pointer %s' %latestAiredPointer)

    # response[latestAiredPointer] is the last aired episode
    # response[latestAiredPointer+1] is the next episode (if it exists)
    # if latestAiredPointer is -1 then it means that there is no data for any future episodes
    return latestAiredPointer

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

def createEventRule(ruleName,seriesName,cronjob):
    # Create the rule only if it doesn't already exist
    response = eventClient.list_rules()
    logger.info('List Rules Response: %s' %response)
    for rule in response['Rules']:
        if ruleName in rule.values():
            logger.info('%s rule already exists' %ruleName)
            return
    response = eventClient.put_rule(Name=ruleName, ScheduleExpression=cronjob, State='ENABLED', Description='Notification for '+seriesName,)
    logger.info('Put Rule Response: %s' %response)

def putTargetToEventRule(ruleName, eventInput):
    # Put target only if its not already attached
    response = eventClient.list_targets_by_rule(Rule=ruleName)
    logger.info('List Targets Response: %s' %response)
    for target in response['Targets']:
        if NOTIFICATION_LAMBDA_ARN in target.values():
            logger.info('%s target already exists' %NOTIFICATION_LAMBDA_ARN)
            return
    response = eventClient.put_targets( Rule=ruleName,
                                        Targets=[{  'Arn': NOTIFICATION_LAMBDA_ARN,
                                                    'Id': PROJECT_NAME+'-'+ENVIRONMENT+'-notification-lambda',
                                                    'Input': json.dumps(eventInput)}])
    logger.info('Put Targets Response: %s' %response)

def setupNotification(seriesName, episode, date):
    ruleName=PROJECT_NAME+'-'+ENVIRONMENT+'-'+seriesName.replace(' ', '-')+'-'+episode+'-'+date   
    if CUSTOM_CRON_JOB=='':
        dateList=date.split('-')
        cronjob = 'cron(30 10 ' + dateList[2] + ' ' + dateList[1] + ' ? '+ dateList[0]+')'
    else:
        cronjob = CUSTOM_CRON_JOB
    eventInput = {
        "Rule Name": ruleName,
        "Name": seriesName,
        "Episode": episode,
        "Episode Date": date
    }
    
    logger.info('Creating Event Rule for: %s' %eventInput)
    logger.info('cronjob: %s' %cronjob)

    createEventRule(ruleName,seriesName,cronjob)
    putTargetToEventRule(ruleName, eventInput)
    logger.info('Successfully set Event rule for %s' %seriesName)

nextDates = []
nextEp    = []
prevDates = []
prevEp    = []
# Get Latest information for all the series in the List
for s in series['SeriesList']:
    id=s['SeriesID']    
    logger.info('id: %s' %id)
    # Return a sorted json with all the episodes of the tv series
    response = get(BASE_URL+'/shows/'+id+'/episodes').json()
    logger.info('%s' %response)

    latestAiredPointer = findlatestAiredEpisode(response)

    prevEp.append(getEpisodesFromEpisodeList(response, latestAiredPointer))
    nextEp.append(getEpisodesFromEpisodeList(response, latestAiredPointer+1))
    prevDates.append(getDatesFromEpisodeList(response, latestAiredPointer))
    nextDates.append(getDatesFromEpisodeList(response, latestAiredPointer+1))

seriesNamesList =[s['SeriesName'] for s in series['SeriesList']] 

# Sort, Combine and Transpose List
nextDates, seriesNamesList, nextEp, prevDates, prevEp = zip(*sorted(zip(nextDates, seriesNamesList, nextEp, prevDates, prevEp)))
transposedList = list(map(list, zip(*[seriesNamesList, prevEp, prevDates, nextEp, nextDates])))

def lambda_handler(event, context):
    data = tabulate(transposedList, headers=['Name', 'Prev. Ep.','Airtime','Next Ep.','Airtime'], 
                                    colalign=("left","center","left","center","center"), tablefmt="html")
    response = sendSESEmail(data)
    logger.info('SES Response: %s' %response)

    # Create Notification Event Rule for the upcoming episodes
    for i in range(0,len(nextDates)):
        if nextDates[i]!='N/A':
            setupNotification(series[i],nextEp[i],nextDates[i])
