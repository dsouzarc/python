#!/usr/bin/python

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

#Gets the title HTML tag
titleStart = rawhtml.find("<title>", 0);
titleEnd = rawhtml.find("</title>", 0);
tempTitle = rawhtml[titleStart:titleEnd];

#Gets the image's actual title
titleStart = tempTitle.find(" | ", 0) + 3;
titleEnd = tempTitle.find(" | Flickr", 0);
title = tempTitle[titleStart:titleEnd];

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

#Go to the link, get the photo and save it as a 'jpg' with the image's flickr title
urllib.urlretrieve(url, title + ".jpg");

#Success
print("Successfully downloaded: " + title);
