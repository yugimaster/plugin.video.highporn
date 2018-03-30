#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from common import *

HOST = "https://xxx.xcity.jp"
IDOLSTAPI = "/idol/"


class Xcity(object):
    """docstring for Xcity"""
    def __init__(self):
        pass

    def idol(self):
        url = HOST + IDOLSTAPI
        data = GetHttpData(url)
        if not data or data == '{"status": "Fail"}':
            return None
        soup = BeautifulSoup(data, 'html.parser')
        return soup

    def search(self, keyword):
        url = HOST + IDOLSTAPI + "?genre=/idol/&q={0}&sg=idol&num=30".format(keyword)
        data = GetHttpData(url)
        if not data or data == '{"status": "Fail"}':
            return None
        soup = BeautifulSoup(data, 'html.parser')
        return soup

    def detail(self, url):
        data = GetHttpData(url)
        if not data or data == '{"status": "Fail"}':
            return None
        soup = BeautifulSoup(data, 'html.parser')
        return soup
