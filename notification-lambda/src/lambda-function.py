import json
import boto3
import os
import logging

EMAIL_SUBJECT = 'New Episode Available today'
SRC_EMAIL     = os.environ['SRC_EMAIL']
DST_EMAIL     = os.environ['DST_EMAIL']
client        = boto3.client('ses')
eventClient   = boto3.client('events')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def sendSESEmail(data):
    response = client.send_email(Source=SRC_EMAIL,Destination={'ToAddresses': [DST_EMAIL],},
                                Message={
                                    'Body': {
                                        'Html': {'Charset': 'UTF-8', 'Data': data,}
                                        },
                                    'Subject': { 'Charset': 'UTF-8', 'Data': EMAIL_SUBJECT}
                                    })
    return response['ResponseMetadata']['HTTPStatusCode']

def removeEventRule(ruleName):
    # Remove target from Rule
    eventTargetId = eventClient.list_targets_by_rule(Rule=ruleName)['Targets'][0]['Id']
    logger.info('Event Target Id: %s' %eventTargetId)
    response = eventClient.remove_targets(Rule=ruleName, Ids=[eventTargetId])
    logger.info('Remove Target Response: %s' %response)
    
    # Delete Rule
    response = eventClient.delete_rule(Name=ruleName)
    logger.info('Delete Rule Response: %s' %response)

def lambda_handler(event, context):
    # Retrieve information about series name and episode
    logger.info('%s' %event)

    # Send Notification Email
    data = 'New episode for '+ event['Name'] + ', episode: '+ event['Episode']
    response = sendSESEmail(data)
    logger.info('SES Response: %s' %response)

    # Remove Event Rule
    removeEventRule(event['Rule Name'])
