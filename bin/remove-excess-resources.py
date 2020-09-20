import boto3
from argparse import ArgumentParser
logsClient = boto3.client('logs')
eventsClient = boto3.client('events')

def parse_args():
    parser = ArgumentParser(description='Update Lambda Environment Variables')
    parser.add_argument('-p', '--project-name', type=str,
                        help='Provide the The project name')
    parser.add_argument('-e', '--environment', type=str,
                        help='Provide the environment stage')
    return parser.parse_args()

def removeExcessCloudwatchLogGroups(projectName, environment):
    paginator = logsClient.get_paginator('describe_log_groups')
    prefix = '/aws/lambda/' + projectName + '-' + environment
    print ('Searching for log groups with prefix: ' + prefix)
    
    page_iterator = paginator.paginate(logGroupNamePrefix=prefix)
    for page in page_iterator:
        for logGroup in page['logGroups']:
            print ('Removing the following excess log group: ' + str(logGroup))
            response = logsClient.delete_log_group(logGroupName=logGroup['logGroupName'])
            print (response)

def removeEventRule(ruleName):
    # Remove target from Rule
    eventTargetId = eventsClient.list_targets_by_rule(Rule=ruleName)['Targets'][0]['Id']
    print('Event Target Id: %s' %eventTargetId)
    response = eventsClient.remove_targets(Rule=ruleName, Ids=[eventTargetId])
    print('Remove Target Response: %s' %response)
    
    # Delete Rule
    response = eventsClient.delete_rule(Name=ruleName)
    print('Delete Rule Response: %s' %response)

def removeExcessEventRules(projectName, environment):
    paginator = eventsClient.get_paginator('list_rules')
    prefix = projectName + '-' + environment
    print ('Searching for event rules with prefix: ' + prefix)
    
    page_iterator = paginator.paginate(NamePrefix=prefix)
    for page in page_iterator:
        for eventRules in page['Rules']:
            print ('Removing the following excess events rule: ' + str(eventRules))
            removeEventRule(eventRules['Name'])

if __name__ == "__main__":
    args = parse_args()
    print(vars(args))

    removeExcessCloudwatchLogGroups(args.project_name, args.environment)
    removeExcessEventRules(args.project_name, args.environment)