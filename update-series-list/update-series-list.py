from requests import get
import boto3
from argparse import ArgumentParser
import os
client = boto3.client('lambda')
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def parse_args():
    parser = ArgumentParser(description='Update Lambda Environment Variables')
    parser.add_argument('-f', '--filename', nargs='+', type=str, default='myseries.txt',
                        help='Provide the filename of where the series names are stored')
    parser.add_argument('-l', '--lambdaname', type=str,  default='test-airtime',
                        help='Provide the name of the lamdba function')
    parser.add_argument('-u', '--baseurl', type=str, default='http://api.tvmaze.com/singlesearch/shows?q=',
                        help='Provide the name of the lamdba function (def http://api.tvmaze.com/singlesearch/shows?q=)')
    parser.add_argument('-g', '--getserieslist',  action='store_true',
                        help='Select if you want to retrieve the series list from the Lambda Environment Variables (This choise will overwrite your existing file unless you provide a different filename)')
    return parser.parse_args()

def readSeries(filename):
    return [line.strip() for line in open(os.path.join(__location__, filename))]

def getSeriesIds(series, baseUrl):
    return [str( get(baseUrl+s).json()['id'] ) for s in series]

def updateFunction(series,ids,lambdaName):
    env = client.get_function_configuration(FunctionName = lambdaName)['Environment']
    env['Variables']['SERIES_LIST'] = ','.join(series)
    env['Variables']['IDS_LIST'] = ','.join(ids)
    return str(client.update_function_configuration(FunctionName = lambdaName, Environment = env)['ResponseMetadata']['HTTPStatusCode'])
    
if __name__ == "__main__":
    args = parse_args()
    print(vars(args))
    
    if args.getserieslist:
        print ('Retrieving series list...') 
        #Implement get series list function
    else:
        print ('Updating series list...')
        series = readSeries(args.filename)
        print ('Series: '+str(series))

        ids = getSeriesIds(series, args.baseurl)
        print ('IDs: '+str(ids))

        response = updateFunction(series, ids, args.lambdaname)
        print ('Response Code: ' + response)