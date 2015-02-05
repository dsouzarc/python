#!/usr/bin/python

import datetime;
import re;
import sys;
import urllib;
import urllib2;

#Written by Ryan D'souza
#Receives the URL to a beautiful picture hosted on Flickr that cannot be downloaded
#Finds the API link that holds the picture
#Downloads the picture to the directory based on that link

#If the link is a commandline argument
if len(sys.argv) == 2:
    pageHTML = urllib2.urlopen(sys.argv[1]);

#Else, input it
else:
    pageHTML = urllib2.urlopen(raw_input("Enter flickr link: "));

#Get the HTML from the flickr page
rawhtml = pageHTML.read();

#Start and end of the image tag
startindex = rawhtml.find('<img src="https://farm', 0);
endindex = rawhtml.find('<p id="faq-link" class="info">', 0);

#String for the image tag
imgtag = rawhtml[startindex:endindex];

#Find the link in that image tag
startindex = imgtag.find('http', 0);
endindex = imgtag.find('">', 2);

#The link
url = imgtag[startindex:endindex]; 

#Go to the link, get the photo and save it as a 'jpg' with today's time and date as the file name
urllib.urlretrieve(url, "Flickr from " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y" + ".jpg"));
