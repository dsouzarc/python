import re;
import json;
import sys;
import urllib;
import urllib2;

tempURL = "http://www.reddit.com/r/winterporn/top.json?sort=top&t=all";

response = urllib2.urlopen(tempURL);
response = json.load(response);

jsonPosts = response["data"]["children"];
redditPosts = {};

for jsonPost in jsonPosts:
    jsonPost = jsonPost["data"];
    domain = jsonPost["domain"];
    score = jsonPost["score"];
    title = jsonPost["title"];
    url = jsonPost["url"];

    print(title);


    class RedditPost(object):
        domain = None;
        score = None;
        title = None;
        url = None;

        def __init__(self, domain, score, title, url):
            self.domain = domain;
            self.score = score;
            self.title = title;
            self.url = url;
