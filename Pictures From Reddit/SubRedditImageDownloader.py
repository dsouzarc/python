import re;
import json;
import sys;
import urllib;
import urllib2;

class SubRedditImageDownloader:

        generatedURL = None;
        redditPosts = None;

        maxNumberOfPhotos = None;
        minUpvotes = None;
        minPhotoWidth = None;
        minPhotoHeight = None;

        def __init__(self, subreddit, maxNumberOfPhotos=10000, minUpvotes=0, minPhotoWidth=1280, minPhotoHeight=800):
            self.generatedURL = "http://www.reddit.com/r/" + subreddit + "/top.json?sort=top&t=all";
            self.redditPosts = [];

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
