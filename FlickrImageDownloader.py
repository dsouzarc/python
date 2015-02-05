#!/usr/bin/python

import urllib2;
import sys;

#Written by Ryan D'souza
#Receives the URL to a beautiful picture hosted on Flickr that cannot be downloaded
#Finds the API link that holds the picture
#Downloads the picture to the directory based on that link

#If the link is a commandline argument
if len(sys.argv) == 2:
    response = urllib2.urlopen(sys.argv[1]);

#Else, input it
else:
    response = urllib2.urlopen(raw_input("Enter flickr link: "));

#Print result for now
print(response.read());
