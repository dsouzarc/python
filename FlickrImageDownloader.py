#!/usr/bin/python

import urllib2;
import sys;
import re;

def parse(html, *atrs):
    soup= BeautifulSoup(html)
    body = soup.find(*atrs)
    return body

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

#Print result for now
#print(pageHTML.read());


rawhtml = pageHTML.read();
#print(rawhtml);

startindex = rawhtml.find("allsizes-photo", 10);

print(rawhtml.find("allsizes-photo", 50));
print(rawhtml[startindex:startindex+50]);
