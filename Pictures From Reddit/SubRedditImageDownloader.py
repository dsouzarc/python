from StringIO import *;

import json;
import random;
import requests;
import struct
import sys;
import urllib;
import urllib2;
import warnings

#####################################################################

# Written by Ryan D'souza
#
# Downloads photos from subreddits with the correct
# file name and file type in the best resolution possible
# Even downloads from annoying flickr links
#
# Dependencies:
#   None except for the above imports
#
# Run Instructions:
#   python SubRedditImageDownloader.py

#####################################################################


class SubRedditImageDownloader:

        #Program specific variables
        generatedURL = None;
        redditPosts = None;
        numberOfSavedPhotos = None;
        userAgents = None;
        userAgent = None;
        counter = None;

        #Class/User customizable variables
        maxNumberOfPhotos = None;
        minUpvotes = None;
        minPhotoWidth = None;
        minPhotoHeight = None;

        def __init__(self, subreddit, maxNumberOfPhotos=10000, minUpvotes=0, minPhotoWidth=600, minPhotoHeight=600):
            self.generatedURL = "http://www.reddit.com/r/" + subreddit + "/top.json?sort=top&t=all";
            self.redditPosts = [];
            self.numberOfSavedPhotos = 0;
            self.userAgents = [];
            self.counter = 0;

            #Disable python warnings --> usually about an improper SSL handshake. 
            warnings.filterwarnings("ignore")

            #Add 50 random UserAgents to the array and choose one
            with open('50useragents.txt', 'r') as userAgentsFile:
                for userAgent in userAgentsFile:
                    self.userAgents.append(userAgent);
            self.userAgent = random.choice(self.userAgents);

            self.maxNumberOfPhotos = maxNumberOfPhotos;
            self.minUpvotes = minUpvotes;
            self.minPhotoWidth = minPhotoWidth;
            self.minPhotoHeight = minPhotoHeight;

            #Get the first page of Posts
            self.getRedditPosts(self.generatedURL);

        #Gets the Posts from the URL and begins downloading them. Is recursive
        def getRedditPosts(self, redditURL):
            self.userAgentHandler();
            response = urllib2.urlopen(self.getURLLibRequest(redditURL)).read();
            response = json.loads(response);

            data = response["data"];
            jsonPosts = data["children"];

            #For each post on the page, get the info and save it to the array
            for jsonPost in jsonPosts:
                jsonPost = jsonPost["data"];
                domain = jsonPost["domain"];
                score = jsonPost["score"];
                title = jsonPost["title"];
                url = jsonPost["url"];

                redditPost = RedditPost(domain, score, title, url);
                self.redditPosts.append(redditPost);

                #Get the post's actual image URL and save that photo
                actualURL = self.getPhotoURL(redditPost);
                self.savePhoto(redditPost, actualURL);

            #Check number of photos condition to see if we should continue
            if self.maxNumberOfPhotos != 0 and self.numberOfSavedPhotos >= self.maxNumberOfPhotos:
                return;
            
            #Checks min upvotes condition to see if we should continue
            if self.minUpvotes != 0 and self.redditPosts[-1].score <= self.minUpvotes:
                return;

            #We should continue
            afterToken = data["after"];
            if len(afterToken) <= 3:
                print("NO MORE IMAGES");
            else:
                redditURL += "&after=" + afterToken;
                print("Getting next page...");

                #Recursively get more posts to save
                self.getRedditPosts(redditURL);

        #Handles dealing with the user agent - every 10 requests, change it
        def userAgentHandler(self):
            self.counter += 1;
            if self.counter % 10 == 0:
                self.userAgent = random.choice(self.userAgents);

        #Generates the URL request with the user agent
        def getURLLibRequest(self, url):
            request = urllib2.Request(url, headers={ 'User-Agent': self.userAgent});
            return request;

        #Gets the image's actual URL - it's different depending on the site
        def getPhotoURL(self, redditPost):

            #i.imgur.com is plain and simple
            if redditPost.domain == 'i.imgur.com':
                return redditPost.url;

            #imgur.com requires a download tag to be appended
            if redditPost.domain == 'imgur.com':
                return redditPost.url.replace("imgur.com/", "imgur.com/download/");

            #Any form of flickr requires special parsing to get the photo's actual URL
            if redditPost.domain == 'flickr.com':
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.5.17 (KHTML, like Gecko) Version/8.0.5 Safari/600.5.17"
                };
                response = requests.get(redditPost.url, headers=headers);
                response = response.content.replace("\n", "");
                jsonBegin = response.find("modelExport: ", 0) + 12;
                jsonEnd = response.find("auth: auth,", 0) - 3;

                #The first type of Flickr photo/url
                try:
                    jsonResult = json.loads(response[jsonBegin:jsonEnd]);
                    photoSizes = jsonResult["photo-models"];
                    photoSizes = photoSizes[0]["sizes"];

                    #First try to get the original photo, then large, then 'c' size
                    if 'o' in photoSizes:
                        return "http:" + photoSizes["o"]["url"];
                    if 'l' in photoSizes:
                        return "http:" + photoSizes["l"]["url"];
                    if 'c' in photoSizes:
                        return "http:" + photoSizes["c"]["url"];
                    else
                        print("NO PHOTO SIZE FOUND: " + redditPost.title + "\t" + redditPost.url);

                #If this way doesn't work, there's another type of Flickr tag we can download
                except ValueError:
                    try:
                        #Start and end of the image tag
                        startindex = response.find('<img src="https://farm', 0);
                        endindex = response.find('<p id="faq-link" class="info">', 0);
                        imgtag = response[startindex:endindex];

                        #Find the link in that image tag
                        startindex = imgtag.find('http', 0);
                        endindex = imgtag.find('">', 2);
                        url = imgtag[startindex:endindex]; 
                        return url;
                    except:
                        print("\nERROR GETTING IMAGE: " + redditPost.title + "\tURL: " + redditPost.url + "\n");
                        return redditPost.url;

            #If it's nothing we're familiar with
            else:
                return redditPost.url;

        #Saves the photo with the image's name as the file's name
        def savePhoto(self, redditPost, actualURL):
            print("Reading: " + redditPost.title + "\tURL: " + actualURL);

            try:
                self.userAgentHandler();
                image = urllib2.urlopen(self.getURLLibRequest(actualURL)).read();
            except IOError:
                print("ERROR AT: " + redditPost.title + "\tURL: " + actualURL);
                return;

            #The image dimensions
            imageInfo = self.get_image_info(image);

            #Check to make sure the image dimensions match the minimums
            if imageInfo["width"] >= self.minPhotoWidth and imageInfo["height"] >= self.minPhotoHeight:

                #And that the score is greater than the minimum
                if redditPost.score >= self.minUpvotes:

                    #And that we haven't passed our max number of photos. For now, just download everything
                    if self.maxNumberOfPhotos != 0 and self.numberOfSavedPhotos <= self.maxNumberOfPhotos or 1 == 1:

                        #Except images that no longer exist --> symbolized by special image
                        if imageInfo["width"] == 161 and imageInfo["height"] == 81 and imageInfo["content-type"] == ".png":
                            print("NO LONGER EXISTS: \t" + actualURL);
                            return;

                        #Fix the file name - replace '\', shorten title if it's too long, add image type at the end
                        fileName = redditPost.title.replace("/", "").replace("\\", "");
                        if len(fileName) > 245:
                            fileName = fileName[0:245];
                        fileName += imageInfo["content_type"];

                        #Save the image if it's a valid content-type
                        if len(imageInfo["content_type"]) > 2:
                            with open(fileName, 'w') as imageFile:
                                imageFile.write(image);
                                imageFile.close();
                                print("Successfully saved: " + fileName);
                                self.numberOfSavedPhotos += 1;

                        #Otherwise, it's an album
                        else:
                            print("\nALBUM: " + redditPost.title + "\t" + redditPost.url + "\n");
                    else:
                        print("Max hit: " + redditPost.title);
                else:
                    print("Not enough upvotes: " + redditPost.title);
            else:
                print("TOO SMALL: " + str(imageInfo["width"]) + "\tHeight: " + str(imageInfo["height"]) + "\t" + redditPost.title + "\t" + redditPost.url);

        #Returns a dictionary with the image's info: width, height, contenttype
        def get_image_info(self, data):
            data = str(data)
            size = len(data)
            height = -1
            width = -1
            content_type = ''

            # handle GIFs
            if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
                # Check to see if content_type is correct
                content_type = '.gif'
                w, h = struct.unpack("<HH", data[6:10])
                width = int(w)
                height = int(h)

            # See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
            elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
                  and (data[12:16] == 'IHDR')):
                content_type = '.png'
                w, h = struct.unpack(">LL", data[16:24])
                width = int(w)
                height = int(h)

            # Maybe this is for an older PNG version.
            elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
                # Check to see if we have the right content type
                content_type = '.png'
                w, h = struct.unpack(">LL", data[8:16])
                width = int(w)
                height = int(h)

            # Handle JPEGs
            elif (size >= 2) and data.startswith('\377\330'):
                content_type = '.jpeg'
                jpeg = StringIO(data)
                jpeg.read(2)
                b = jpeg.read(1)
                try:
                    while (b and ord(b) != 0xDA):
                        while (ord(b) != 0xFF): b = jpeg.read
                        while (ord(b) == 0xFF): b = jpeg.read(1)
                        if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                            jpeg.read(3)
                            h, w = struct.unpack(">HH", jpeg.read(4))
                            break
                        else:
                            jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
                        b = jpeg.read(1)
                    width = int(w);
                    height = int(h)
                    
                except struct.error:
                    print("ERROR GETTING IMAGE DIMENSIONS");
                    pass
                except ValueError:
                    print("ERROR GETTING IMAGE DIMENSIONS");
                    pass

            return {
                "content_type": content_type,
                "width": width,
                "height": height
            };


#Represents a post on Reddit
class RedditPost:
    domain = None;
    score = None;
    title = None;
    url = None;

    def __init__(self, domain, score, title, url):
        self.domain = domain;
        self.score = score;
        self.title = title;
        self.url = url;

#Main method
if __name__ == "__main__":
    downloader = SubRedditImageDownloader(raw_input("Enter subreddit: "));
