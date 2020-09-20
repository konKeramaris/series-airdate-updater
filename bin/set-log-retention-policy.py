import boto3
from argparse import ArgumentParser
client = boto3.client('logs')

def parse_args():
    parser = ArgumentParser(description='Update Lambda Environment Variables')
    parser.add_argument('-p', '--project-name', type=str,
                        help='Provide the The project name')
    parser.add_argument('-e', '--environment', type=str,
                        help='Provide the environment stage')
    parser.add_argument('-r', '--retention-policy', type=str,default=60,
                        help='Provide the environment stage')
    return parser.parse_args()

def setCloudwatchLogGroupsRetentionPolicy(projectName, environment, retentionPolicy):
    paginator = client.get_paginator('describe_log_groups')
    prefix='/aws/lambda/'+projectName+'-'+environment
    print ('Searching for log groups with prefix: ' + prefix)
    
    page_iterator = paginator.paginate(logGroupNamePrefix=prefix)
    for page in page_iterator:
        for logGroup in page['logGroups']:
            print (logGroup)
            if ('retentionInDays' not in logGroup.keys()) or (logGroup['retentionInDays'] != retentionPolicy):
                print ('Incorrect Retention Policy, setting up the correct one ...')
                response = client.put_retention_policy(logGroupName=logGroup['logGroupName'],retentionInDays=retentionPolicy)
                print (response)
            else:
                print ('Correct Retentions Policy, nothing to do')

if __name__ == "__main__":
    args = parse_args()
    print(vars(args))

    setCloudwatchLogGroupsRetentionPolicy(args.project_name, args.environment, args.retention_policy)
