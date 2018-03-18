#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import traceback
import threading
import time
from functools import wraps


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


def run_async(func):
    """
    Decorator to run a function in a separate thread
    """
    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = threading.Thread(target=func,
                                   args=args,
                                   kwargs=kwargs)
        func_hl.start()
        return func_hl

    return async_func


def GetDateTimeString():
    str_ymd = time.strftime("%Y/%m/%d")
    str_hms = time.strftime("%H:%M:%S")
    str_date = str_ymd + " " + str_hms
    return str_date
