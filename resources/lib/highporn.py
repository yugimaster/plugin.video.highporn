#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from common import *

HOST = "http://highporn.net"
SEARCHAPI = "/search/videos?search_query="
PLAYAPI = "/play.php"


class HighPorn(object):
    """docstring for HighPorn"""
    def __init__(self):
        pass

    def index(self):
        url = HOST
        data = GetHttpData(url)
        if not data or data == '{"status": "Fail"}':
            return None
        soup = BeautifulSoup(data, 'html.parser')
        videolist = soup.find_all("div", {"class": "col-sm-6 col-md-4 col-lg-4"})
        return videolist[1:]

    def search(self, keyword, pagenum=1):
        url = HOST + SEARCHAPI + "{0}&page={1}".format(keyword, pagenum)
        print url
        data = GetHttpData(url)
        if not data or data == '{"status": "Fail"}':
            return None
        soup = BeautifulSoup(data, 'html.parser')
        videolist = soup.find_all("div", {"class": "col-sm-6 col-md-4 col-lg-4"})
        return videolist

    def detail(self, url_link):
        url = HOST + url_link
        data = GetHttpData(url)
        if not data or data == '{"status": "Fail"}':
            return None
        soup = BeautifulSoup(data, 'html.parser')
        return soup

    def playurl(self, vid):
        url = HOST + PLAYAPI
        formdata = {"v": vid}
        data = PostHttpData(url, formdata)
        if not data:
            return None
        return data
