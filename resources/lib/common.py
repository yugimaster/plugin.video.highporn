#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import traceback


def colorize(label, color):
    return "[COLOR %s]" % color + label + "[/COLOR]"


def GetHttpData(url, data=None):
    try:
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
        }
        httpdata = requests.get(url, headers=headers).text
    except Exception:
        print_exc()
        httpdata = '{"status": "Fail"}'
    return httpdata


def PostHttpData(url, data=None):
    try:
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
        }
        payload = data
        httpdata = requests.post(url, data=payload, headers=headers).text
    except Exception:
        print_exc()
        httpdata = None
    return httpdata


def print_exc():
    traceback.print_exc()
