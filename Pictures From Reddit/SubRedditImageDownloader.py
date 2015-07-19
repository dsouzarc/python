from StringIO import *
import re;
import struct;
import json;
import sys;
import urllib;
import urllib2;

class SubRedditImageDownloader:

        generatedURL = None;
        redditPosts = None;
        numberOfSavedPhotos = None;

        maxNumberOfPhotos = None;
        minUpvotes = None;
        minPhotoWidth = None;
        minPhotoHeight = None;

        def __init__(self, subreddit, maxNumberOfPhotos=10000, minUpvotes=0, minPhotoWidth=700, minPhotoHeight=700):
            self.generatedURL = "http://www.reddit.com/r/" + subreddit + "/top.json?sort=top&t=all";
            self.redditPosts = [];
            self.numberOfSavedPhotos = 0;

            self.maxNumberOfPhotos = maxNumberOfPhotos;
            self.minUpvotes = minUpvotes;
            self.minPhotoWidth = minPhotoWidth;
            self.minPhotoHeight = minPhotoHeight;

            self.getRedditPosts(self.generatedURL);

        def getRedditPosts(self, redditURL):
            response = urllib2.urlopen(redditURL);
            response = json.load(response);

            jsonPosts = response["data"]["children"];

            for jsonPost in jsonPosts:
                jsonPost = jsonPost["data"];
                domain = jsonPost["domain"];
                score = jsonPost["score"];
                title = jsonPost["title"];
                url = jsonPost["url"];

                redditPost = RedditPost(domain, score, title, url);
                self.redditPosts.append(redditPost);

                actualURL = self.getPhotoURL(redditPost);
                self.savePhoto(redditPost, actualURL);

        def getPhotoURL(self, redditPost):
            #Plain and simple
            if redditPost.domain == 'i.imgur.com':
                return redditPost.url;
            if redditPost.domain == 'imgur.com':
                return redditPost.url.replace("imgur.com/", "imgur.com/download/");
            else:
                return "PROBLEM";

        def savePhoto(self, redditPost, actualURL):
            print("Reading: " + actualURL);
            image = urllib.urlopen(actualURL).read();
            imageInfo = self.get_image_info(image);

            if imageInfo["width"] >= self.minPhotoWidth and imageInfo["height"] >= self.minPhotoHeight:
                if redditPost.score >= self.minUpvotes:
                    if self.maxNumberOfPhotos != 0 and self.numberOfSavedPhotos <= self.maxNumberOfPhotos:
                        fileName = redditPost.title + imageInfo["content_type"];
                        with open(fileName, 'w') as imageFile:
                            imageFile.write(image);
                            imageFile.close();
                            print("Successfully saved: " + fileName);
                    else:
                        print("Max hit");
                else:
                    print("Not enough upvotes");
            else:
                print("Too small: " + str(imageInfo["width"]) + "\tHeight: " + str(imageInfo["height"]));




        def get_image_info(self, data):
            """
            Return (content_type, width, height) for a given img file content
            no requirements
            """
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
            # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
            # and finally the 4-byte width, height
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

            # handle JPEGs
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
                    pass
                except ValueError:
                    pass

            return {
                "content_type": content_type,
                "width": width,
                "height": height
            };

                
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

if __name__ == "__main__":
    downloader = SubRedditImageDownloader("winterporn");
    
