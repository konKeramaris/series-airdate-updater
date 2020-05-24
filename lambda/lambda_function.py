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

def getEpisodesFromShowInfo(showid, key, episodes, dates):
    show = get(BASE_URL+'/shows/'+showid)
    if key in show.json()['_links']:
        epidodeUrl = show.json()['_links'][key]['href']
        response = get(epidodeUrl)
        episodes.append('s'+str(response.json()['season'])+'e'+str(response.json()['number']))
        dates.append(response.json()['airdate'])
    else:
        episodes.append('No Data')
        dates.append('No Data')
    return episodes, dates

def getEpisodesFromEpisodeList(data, index, episodes, dates):
    if index == 0:
        episodes.append('No Data')
        dates.append('No Data')
    else:
        episodes.append('s'+str(data[index]['season'])+'e'+str(data[index]['number']))
        dates.append(data[index]['airdate'])
    return episodes,dates

nextDates = []; nextEp = []; prevDates = []; prevEp = []
for i in ids:
    response = get(BASE_URL+'/shows/'+i+'/episodes')
    if response.json()[-1]['airdate'] =='':
        prevEp, prevDates = getEpisodesFromShowInfo(i, 'previousepisode', prevEp, prevDates)
        nextEp, nextDates = getEpisodesFromShowInfo(i, 'nextepisode', nextEp, nextDates)
    else:
        if response.json()[-1]['airdate'] > str(datetime.now().date()):
            # If episode is later than the current day
            # then show the last previous episode and the upcoming episode
            prevEp, prevDates = getEpisodesFromEpisodeList(response.json(), -2, prevEp, prevDates)
            nextEp, nextDates = getEpisodesFromEpisodeList(response.json(), -1, nextEp, nextDates)
        else:
            prevEp, prevDates = getEpisodesFromEpisodeList(response.json(), -1, prevEp, prevDates)
            nextEp, nextDates = getEpisodesFromEpisodeList(response.json(), 0, nextEp, nextDates)

# Sort, Combine and Transpose List
nextDates, series, nextEp, prevDates, prevEp = zip(*sorted(zip(nextDates, series, nextEp, prevDates, prevEp)))
transposedList = list(map(list, zip(*[series, prevEp, prevDates, nextEp, nextDates])))

def lambda_handler(event, context):    
    response = client.send_email(
        Destination={'ToAddresses': [DST_EMAIL],},
        Message={
            'Body': {'Html': {'Charset': 'UTF-8', 'Data': tabulate(transposedList, headers=['Name', 'Previous Ep.','Airtime','Next Ep.','Airtime'], tablefmt="html"),}},
            'Subject': { 'Charset': 'UTF-8', 'Data': 'Your Weekly Series Airtime Updater',},
        },
        Source=SRC_EMAIL)
    return response['ResponseMetadata']['HTTPStatusCode']