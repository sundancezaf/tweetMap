from urllib.parse import quote_plus
import json
import requests
from requests_oauthlib import OAuth1
import sys
from secrets import *
sys.path.insert(0, './modulesForOauth')


# The code in this file won't work until you set up your Twitter "app"
# at https://dev.twitter.com/apps



# Call this function after starting Python.  It creates a Twitter client object
# (in variable client)that is authorized (based on your account credentials and
# the keys above) to talk to the Twitter API. You won't be able to use the
# other functions in this file until you've called authTwitter()

def authTwitter():
    global client
    client = OAuth1(API_KEY, API_SECRET,ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

def searchTwitter(searchString, count=20, radius=2, latlngcenter=None):
    query = "https://api.twitter.com/1.1/search/tweets.json?q=" + \
        quote_plus(searchString) + "&count=" + str(count) + "&tweet_mode=extended"

    # if you want JSON results that provide full text of tweets longer than 140
    # characters, add "&tweet_mode=extended" to your query string. 
    if latlngcenter != None:
        query = query + "&geocode=" + \
            str(latlngcenter[0]) + "," + str(latlngcenter[1]) + "," + str(radius) + "km"
    global response
    response = requests.get(query, auth=client)
    resultDict = json.loads(response.text)
    # The most important information in resultDict is the value associated with
    # key 'statuses'
    tweets = resultDict['statuses']
    tweetsWithGeoCount = 0
    #for tweetIndex in range(len(tweets)):
        #tweet = tweets[tweetIndex]
        #if tweet['coordinates'] != None:
            #tweetsWithGeoCount += 1
            #print("Tweet {} has geo coordinates.".format(tweetIndex))
    return tweets


# sometimes tweets contain emoji or other characters that can't be
# printed in Python shell, yielding runtime errors when you attempt
# to print.  This function can help prevent that, replacing such charcters
# with '?'s.  E.g. for a tweet, you can do print(printable(tweet['text']))
#
def printable(s):
    result = ''
    for c in s:
        result = result + (c if c <= '\uffff' else '?')
    return result


# ------ Testing ------------
#authTwitter()

#print(searchTwitter('Pizza'))