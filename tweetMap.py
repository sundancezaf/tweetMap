import tkinter
import ssl
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlencode, quote_plus
import json
import webbrowser
from twitteraccess import *
from secrets import *

authTwitter()

# Using a class instead of using global variables
class Globals:
    rootWindow = None
    mapLabel = None
    defaultLocation = "Mauna Kea, Hawaii"
    mapLocation = defaultLocation
    mapFileName = 'googlemap.gif'
    mapSize = 400
    zoomLevel = 9
    mapType = 'roadmap'
    keyword = None
    index = 0
    keywordEntry = None
    locationEntry = None
    keywordString = None
    tweetListLength = None
    numTweetsFoundLabel = None
    tweetButtonLabel = None
    tweetResults = None
    name = None
    nameLabel = None
    username = None
    usernameLabel = None
    URLLabel = None
    URLText = None
    coordList = []
    locationSearch = None
    markers = None
    noCoordsLocation = None
    nextURL = None
    previousURL = None
    urlIndex = 0
    URLlist = []


def changeColorOfLink(event):
    Globals.URLLabel.configure(fg='brown')

# ------------------- Functions for Map -------------------------------------


def geocodeAddress(addressString):
    urlbase = "https://maps.googleapis.com/maps/api/geocode/json?address="
    geoURL = urlbase + quote_plus(addressString)
    geoURL = geoURL + "&key=" + GOOGLEAPIKEY

    # required (non-secure) security stuff for use of urlopen
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    stringResultFromGoogle = urlopen(geoURL, context=ctx).read().decode('utf8')
    jsonResult = json.loads(stringResultFromGoogle)
    if (jsonResult['status'] != "OK"):
        print(
            "Status returned from Google geocoder *not* OK: {}".format(jsonResult['status']))
        # this prevents crash in retrieveMapFromGoogle -
        # yields maps with lat/lon center at 0.0, 0.0
        result = (0.0, 0.0)
    else:
        loc = jsonResult['results'][0]['geometry']['location']
        result = (float(loc['lat']), float(loc['lng']))
    return result


def getMapUrl():
    lat, lng = geocodeAddress(Globals.mapLocation)
    urlbase = "http://maps.google.com/maps/api/staticmap?"
    if Globals.markers != None:
        args = "center={},{}&zoom={}&size={}x{}&maptype={}&format=gif{}".format(
            lat, lng, Globals.zoomLevel, Globals.mapSize, Globals.mapSize, Globals.mapType, Globals.markers)
        args = args + "&key=" + GOOGLEAPIKEY
        mapURL = urlbase + args
        Globals.locationSearch = lat, lng
    else:
        args = "center={},{}&zoom={}&size={}x{}&maptype={}&format=gif".format(
            lat, lng, Globals.zoomLevel, Globals.mapSize, Globals.mapSize, Globals.mapType)
        args = args + "&key=" + GOOGLEAPIKEY
        mapURL = urlbase + args
        Globals.locationSearch = lat, lng
    return mapURL


def retrieveMapFromGoogle():
    url = getMapUrl()
    urlretrieve(url, Globals.mapFileName)


def displayMap():
    retrieveMapFromGoogle()
    mapImage = tkinter.PhotoImage(file=Globals.mapFileName)
    Globals.mapLabel.configure(image=mapImage)
    # next line necessary to "prevent (image) from being garbage collected"
    # http://effbot.org/tkinterbook/label.htm
    Globals.mapLabel.mapImage = mapImage


def generateMarkerString(currentTweetIndex, tweetLatLonList, mapCenterLatLon):
    i = 0
    redLat, redLong = None, None
    finalString = '&markers=color:green|size:small'
    for item in tweetLatLonList:
        if item != None:
            latitude = item[0]
            longitude = item[1]
            if i != currentTweetIndex:
                otherString = "|{},{}".format(latitude, longitude)
                finalString = finalString + otherString
            if i == currentTweetIndex and item != None:
                redLat, redLong = latitude, longitude

        elif item == None:
            if i != currentTweetIndex:
                otherString = "|{},{}".format(
                    mapCenterLatLon[0], mapCenterLatLon[1])
                finalString = finalString + otherString

            if i == currentTweetIndex:
                redLat, redLong = mapCenterLatLon[0], mapCenterLatLon[1]
        i += 1
    redMarkerString = "&markers=color:red|{},{}".format(redLat, redLong)
    return redMarkerString + finalString

# This opens urls found in the tweet


def callback(url):
    webbrowser.open_new(url)

# --------------  Functions for Twitter -------------------------------


def getURLS():
    tweet = Globals.tweetResults[Globals.index]
    entities = tweet['entities']
    urlsEntity = entities['urls']
    if len(urlsEntity) != 0:
        urlsDict = urlsEntity[0]
        finalURL = urlsDict['url']
        Globals.URLlist = finalURL
        printURLS()


def printURLS():
    if type(Globals.URLlist) == list:
        Globals.URLText = Globals.URLlist[Globals.index]
        Globals.URLLabel.configure(text='{}'.format(
            Globals.URLText), justify=tkinter.LEFT, fg='blue')
        Globals.URLLabel.bind(
            "<Button-1>", lambda e: callback(Globals.URLText))
        Globals.URLLabel.bind("<ButtonRelease-1>", changeColorOfLink)

    else:
        Globals.URLText = Globals.URLlist
        Globals.URLLabel.configure(text='{}'.format(
            Globals.URLText), justify=tkinter.LEFT, fg='blue')
        Globals.URLLabel.bind(
            "<Button-1>", lambda e: callback(Globals.URLText))
        Globals.URLLabel.bind("<ButtonRelease-1>", changeColorOfLink)


def nextURL():
    Globals.urlIndex += 1
    printURLS()


def previousURL():
    Globals.urlIndex -= 1
    printURLS()


def getUserSearchTerms():
    Globals.index = 0
    Globals.tweetResults = None
    Globals.markers = None
    Globals.URLlist = []
    Globals.tweetDisplay.configure(text='')
    Globals.usernameLabel.configure(text="")
    Globals.tweetButtonLabel.configure(text='')
    Globals.mapLocation = Globals.locationEntry.get()
    displayMap()
    Globals.noCoordsLocation = geocodeAddress(Globals.mapLocation)
    Globals.keywordString = Globals.keyword.get()
    getResults()
    Globals.locationEntry.delete(0, tkinter.END)
    Globals.keyword.delete(0, tkinter.END)


def getResults():
    Globals.tweetResults = searchTwitter(
        Globals.keywordString, latlngcenter=Globals.noCoordsLocation)
    Globals.tweetListLength = len(Globals.tweetResults)
    if Globals.tweetListLength == 0:
        Globals.tweetDisplay.configure(text='No Tweets Found')
    else:
        Globals.tweetDisplay.configure(
            text='{} Tweets Found \n Press right arrow to view'.format(Globals.tweetListLength))
        Globals.numTweetsFoundLabel.configure(
            text='Number of tweets found: {}'.format(Globals.tweetListLength))

        for item in Globals.tweetResults:
            if 'coordinates' in item and item['coordinates'] != None:
                coords = item['coordinates']
                coords2 = coords['coordinates']
                longitude = coords2[0]
                latitude = coords2[1]
                finalCoords = [latitude, longitude]
                Globals.coordList.append(finalCoords)
            else:
                Globals.coordList.append(None)


def printTweets():
    tweet = Globals.tweetResults[Globals.index]
    Globals.markers = generateMarkerString(
        Globals.index, Globals.coordList, Globals.noCoordsLocation)
    userInfo = tweet['user']
    Globals.username = userInfo['screen_name']
    Globals.name = userInfo['name']

    getURLS()
    tweetText = tweet['full_text']
    Globals.tweetDisplay.configure(text=tweetText)

    Globals.usernameLabel.configure(text="@{}".format(Globals.username))
    Globals.nameLabel.configure(text="{}".format(Globals.name))
    Globals.tweetButtonLabel.configure(
        text='{}/{}'.format(Globals.index+1, Globals.tweetListLength), fg='brown')
    displayMap()


def previousTweet():
    if Globals.index == None:
        printTweets()
        Globals.tweetButtonLabel.configure(
            text='{}/{}'.format(Globals.index, Globals.tweetListLength), fg='brown')
    else:
        if Globals.index - 1 > -1:
            Globals.index -= 1
            Globals.tweetButtonLabel.configure(
                text='{}/{}'.format(Globals.index, Globals.tweetListLength), fg='brown')
            printTweets()
        else:
            Globals.tweetDisplay.configure(
                text='No more tweets to Display\n Please press right arrow\n for next tweet')
            Globals.tweetButtonLabel.configure(
                text='{}/{}'.format(0, Globals.tweetListLength), fg='brown')
            Globals.usernameLabel.configure(text="".format(Globals.username))
            Globals.nameLabel.configure(text="".format(Globals.name))


def nextTweet():
    if Globals.index == None:
        Globals.index = 0
        printTweets()
    else:
        if Globals.index + 1 <= Globals.tweetListLength:
            printTweets()
            Globals.index += 1
        else:
            Globals.tweetDisplay.configure(
                text='No more tweets to display \n Please press left arrow\n for previous')
            Globals.tweetButtonLabel.configure(
                text='{}/{}'.format(0, Globals.tweetListLength), fg='brown')
            Globals.usernameLabel.configure(text="".format(Globals.username))
            Globals.nameLabel.configure(text="".format(Globals.name))

# ---------- Functions for Map Buttons --------------------------


def zoomIn():
    Globals.zoomLevel = Globals.zoomLevel + 1
    displayMap()


def zoomOut():
    Globals.zoomLevel = Globals.zoomLevel - 1
    displayMap()


def satelliteMaptype():
    Globals.mapType = 'satellite'
    displayMap()


def roadmapMaptype():
    Globals.mapType = 'roadmap'
    displayMap()


def terrainMaptype():
    Globals.mapType = 'terrain'
    displayMap()


def hybridMaptype():
    Globals.mapType = 'hybrid'
    displayMap()

# ------------------------ GUI --------------------------------------------------------------


def initializeGUIetc():
    global choiceVar
    Globals.rootWindow = tkinter.Tk()
    Globals.rootWindow.title("DS11")
    choiceVar = tkinter.StringVar()
    Globals.rootWindow.geometry("1000x620")
    Globals.rootWindow.resizable(0, 0)

    # Frames utilized inside main frame to make design easier
    # ------------------------------- Main Frame -------------------------------------------
    bigGrid = tkinter.Frame(Globals.rootWindow)
    bigGrid.grid(row=0, column=0)

    # -------- 1st Row: Keyword label & entry, Location label & entry, Search Button ------
    entryFrame = tkinter.Frame(bigGrid)
    entryFrame.grid(row=1, column=0, columnspan=8)

    keywordLabel = tkinter.Label(
        entryFrame, text='keyword:', font='Calibri 14')
    locationLabel = tkinter.Label(
        entryFrame, text='Location:', font='Calibri 14')
    Globals.keyword = tkinter.Entry(entryFrame, font='Calibri 14')
    Globals.locationEntry = tkinter.Entry(
        entryFrame, font='Calibri 14', justify=tkinter.LEFT)
    getUserSearchTermsButton = tkinter.Button(
        entryFrame, text='Search', command=getUserSearchTerms, font='Calibri 12')

    keywordLabel.pack(side=tkinter.LEFT, padx=10)
    Globals.keyword.pack(side=tkinter.LEFT, ipadx=10, padx=20)
    locationLabel.pack(side=tkinter.LEFT, padx=10)
    Globals.locationEntry.pack(side=tkinter.LEFT, ipadx=10, padx=10)
    getUserSearchTermsButton.pack(side=tkinter.LEFT, ipadx=30, padx=20)

    # ------------------ 2nd Row:  Radio Buttons map choices --------------------------
    radioButtonsFrame = tkinter.Frame(bigGrid)
    radioButtonsFrame.grid(row=2, column=1, columnspan=4)

    roadmapChoice = tkinter.Radiobutton(
        radioButtonsFrame, text='roadmap', variable=choiceVar, value='1', font='Calibri 12', command=roadmapMaptype)
    satelliteChoice = tkinter.Radiobutton(
        radioButtonsFrame, text='satellite', variable=choiceVar, value='2', font='Calibri 12', command=satelliteMaptype)
    hybridChoice = tkinter.Radiobutton(
        radioButtonsFrame, text='hybrid', variable=choiceVar, value='3', font='Calibri 12', command=hybridMaptype)
    terrainChoice = tkinter.Radiobutton(
        radioButtonsFrame, text='terrain', variable=choiceVar, value='4', font='Calibri 12', command=terrainMaptype)

    roadmapChoice.pack(side=tkinter.LEFT)
    satelliteChoice.pack(side=tkinter.LEFT)
    hybridChoice.pack(side=tkinter.LEFT)
    terrainChoice.pack(side=tkinter.LEFT)

    # ---------------------- 4th Row: Screen name, Name Labels -----------------------
    userInfoFrame = tkinter.Frame(bigGrid)
    userInfoFrame.grid(row=4, column=0, columnspan=3)

    usernameInfo = tkinter.Label(
        userInfoFrame, text='Screen name:', font='Calibri 12')
    Globals.usernameLabel = tkinter.Label(
        userInfoFrame, font='Calibri 12', fg='blue')

    nameInfo = tkinter.Label(userInfoFrame, text='Name:', font='Calibri 12')
    Globals.nameLabel = tkinter.Label(
        userInfoFrame, font='Calibri 12', fg='brown')
    usernameInfo.pack(side=tkinter.LEFT)
    Globals.usernameLabel.pack(side=tkinter.LEFT)
    nameInfo.pack(side=tkinter.LEFT, padx=20)
    Globals.nameLabel.pack(side=tkinter.LEFT)

    # ------------------ 5th Row: Tweet Display Frame, Map Display Frame -------------
    tweetDisplayFrame = tkinter.Frame(bigGrid)
    tweetDisplayFrame.grid(row=5, column=0, columnspan=4)
    mapDisplayFrame = tkinter.Frame(bigGrid)
    mapDisplayFrame.grid(row=5, column=4, columnspan=4)

    Globals.tweetDisplay = tkinter.Label(
        tweetDisplayFrame, text='Please enter a keyword \n and a location', font='Calibri 14', wraplength=250)
    Globals.tweetDisplay.pack(side=tkinter.LEFT)
    Globals.mapLabel = tkinter.Label(mapDisplayFrame, bd=2)
    Globals.mapLabel.pack(side=tkinter.LEFT)

    # ------------------- 6th Row: Num of Tweets found Label ------------------------
    Globals.numTweetsFoundLabel = tkinter.Label(
        bigGrid, text='Number of tweets found: {}'.format(Globals.tweetListLength))
    Globals.numTweetsFoundLabel.grid(row=6, column=0)

    # --------- 8th Row: Previous/Next Tweet Buttons , Zoom in/out Buttons  --------
    tweetsButtonsFrame = tkinter.Frame(bigGrid)
    tweetsButtonsFrame.grid(row=8, column=0, columnspan=4)
    zoomFrame = tkinter.Frame(bigGrid)
    zoomFrame.grid(row=8, column=4, columnspan=4)

    tweetLeftButton = tkinter.Button(
        tweetsButtonsFrame, text='<', font='Calibri 14', command=previousTweet)
    Globals.tweetButtonLabel = tkinter.Label(
        tweetsButtonsFrame, font='Calibri 14')
    tweetRightButton = tkinter.Button(
        tweetsButtonsFrame, text='>', font='Calibri 14', command=nextTweet)
    tweetLeftButton.pack(side=tkinter.LEFT, ipadx=20)
    Globals.tweetButtonLabel.pack(side=tkinter.LEFT, ipadx=20)
    tweetRightButton.pack(side=tkinter.LEFT, ipadx=20)

    zoomInButton = tkinter.Button(
        zoomFrame, text='+', command=zoomIn, font='Calibri 14')
    zoomLabel = tkinter.Label(zoomFrame, text='Zoom', font='Calibri 14')
    zoomOutButton = tkinter.Button(
        zoomFrame, text='-', command=zoomOut, font='Calibri 14')
    zoomInButton.pack(side=tkinter.LEFT, ipadx=10)
    zoomLabel.pack(side=tkinter.LEFT)
    zoomOutButton.pack(side=tkinter.LEFT, ipadx=10)

    # ----------------- 9th row: URL Buttons, URL Display ----------------
    URLButtonsFrame = tkinter.Frame(bigGrid)
    URLButtonsFrame.grid(row=9, column=0, columnspan=5)

    URLTextLabel = tkinter.Label(
        URLButtonsFrame, text='URLs:', font='Calibri 12')
    URLTextLabel.pack(side=tkinter.LEFT)
    Globals.nextURL = tkinter.Button(
        URLButtonsFrame, text='>', command=nextURL)
    Globals.previousURL = tkinter.Button(
        URLButtonsFrame, text='<', command=previousURL)
    Globals.previousURL.pack(side=tkinter.LEFT)
    Globals.nextURL.pack(side=tkinter.LEFT)

    Globals.URLLabel = tkinter.Label(URLButtonsFrame, bd=2, relief=tkinter.SUNKEN,
                                     font='Cambria 12 underline', justify=tkinter.LEFT, cursor='hand1')
    Globals.URLLabel.pack(padx=5, ipadx=200, pady=5, ipady=10)

    choiceVar.set('1')


def startGui():
    initializeGUIetc()
    displayMap()
    Globals.rootWindow.mainloop()

# Testing

startGui()
