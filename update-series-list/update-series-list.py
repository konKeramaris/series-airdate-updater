from requests import get
import boto3
from argparse import ArgumentParser
import os
import json
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
    response = client.put_parameter(Name=name,Value=data,Overwrite=True)
    return str(response['ResponseMetadata']['HTTPStatusCode'])

def saveSeriesToFile(filename, seriesSSMParameter):
    series = json.loads(client.get_parameter(Name=seriesSSMParameter)['Parameter']['Value'])
    with open(os.path.join(__location__, filename), 'w') as f:
        for s in series['SeriesList']:
            f.write("%s\n" % s['SeriesName'])
    print ('Saved list to: '+filename)
    
if __name__ == "__main__":
    args = parse_args()
    print(vars(args))

    seriesSSMParameter = args.project_name + '-' + args.environment + '-series-list'
    
    if args.getserieslist:
        print ('Retrieving series list...') 
        saveSeriesToFile(args.filename, seriesSSMParameter)
    else:
        print ('Updating SSM Parameter from: '+ args.filename)
        series = readSeries(args.filename)
        ids = getSeriesIds(series, args.baseurl)

        seriesList=[{"SeriesName": series[i], "SeriesID": ids[i]} for i in range(0,len(series))]
        seriesDict={"SeriesList": seriesList}
        print ('New series object')
        print (seriesDict)

        response = updateSSMParameter(seriesSSMParameter, json.dumps(seriesDict))
        print ('[Update Names List] Response Code: ' + response)