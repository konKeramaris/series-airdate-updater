from requests import get
import boto3
from argparse import ArgumentParser
import os
client = boto3.client('ssm')
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def parse_args():
    parser = ArgumentParser(description='Update Lambda Environment Variables')
    parser.add_argument('-p', '--project-name', type=str,
                        help='Provide the The project name')
    parser.add_argument('-e', '--environment', type=str,
                        help='Provide the environment stage')
    parser.add_argument('-f', '--filename', type=str, default='myseries.txt',
                        help='Provide the filename of where the series names are stored')
    parser.add_argument('-u', '--baseurl', type=str, default='http://api.tvmaze.com/singlesearch/shows?q=',
                        help='Provide the name of the lambda function (def http://api.tvmaze.com/singlesearch/shows?q=)')
    parser.add_argument('-g', '--getserieslist',  action='store_true',
                        help='Select if you want to retrieve the series list from the Lambda Environment Variables (This choice will overwrite your existing file unless you provide a different filename)')
    return parser.parse_args()
def readSeries(filename):
    return [line.strip() for line in open(os.path.join(__location__, filename))]

def getSeriesIds(series, baseUrl):
    return [str( get(baseUrl+s).json()['id'] ) for s in series]

def updateSSMParameter(name, data):
    strData = ','.join(data)
    response = client.put_parameter(Name=name,Value=strData,Overwrite=True)
    return str(response['ResponseMetadata']['HTTPStatusCode'])

def saveSeriesToFile(filename, seriesIdsParameter):
    series = client.get_parameter(Name=seriesIdsParameter)['Parameter']['Value'].split(',')
    with open(os.path.join(__location__, filename), 'w') as f:
        for item in series:
            f.write("%s\n" % item)
    print ('Saved list to: '+filename)
    
if __name__ == "__main__":
    args = parse_args()
    print(vars(args))

    seriesNamesParameter = args.project_name + '-' + args.environment + '-name-list'
    seriesIdsParameter = args.project_name + '-' + args.environment + '-ids-list'
    
    if args.getserieslist:
        print ('Retrieving series list...') 
        saveSeriesToFile(args.filename, seriesIdsParameter)
    else:
        print ('Updating SSM Parameter from: '+ args.filename)
        series = readSeries(args.filename)
        print ('Series \t: '+str(series))

        ids = getSeriesIds(series, args.baseurl)
        print ('IDs \t: '+str(ids))

        response = updateSSMParameter(seriesNamesParameter, series)
        print ('[Update Names List] Response Code: ' + response)

        response = updateSSMParameter(seriesIdsParameter, ids)
        print ('[Update Ids List] Response Code: ' + response)