from requests import get
import boto3
import argparse
import os
client = boto3.client('lambda')
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def parse_args():
    parser = argparse.ArgumentParser(description='Update Lambda Environment Variables')
    parser.add_argument('-f', '--filename', nargs='+', type=str,
                        help='Provide the filename of where the series names are stored', default='myseries.txt')
    parser.add_argument('-l', '--lambdaname', type=str,
                        help='Provide the name of the lamdba function', default='test-airtime')
    parser.add_argument('-u', '--baseurl', type=str,
                        help='Provide the name of the lamdba function (def http://api.tvmaze.com/singlesearch/shows?q=)', default='http://api.tvmaze.com/singlesearch/shows?q=')
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

    series = readSeries(args.filename)
    print ('Series: '+str(series))

    ids = getSeriesIds(series, args.baseurl)
    print ('IDs: '+str(ids))

    response = updateFunction(series, ids, args.lambdaname)
    print ('Response Code: ' + response)
