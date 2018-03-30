#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import xbmc
import xbmcgui
import webbrowser


def open_web_browser(urls):
    dialog = xbmcgui.Dialog()
    selected = dialog.select('Choose an url', urls)
    url = urls[selected]
    webbrowser.open_new(url)

    osWin = xbmc.getCondVisibility('System.Platform.Windows')
    osAndroid = xbmc.getCondVisibility('System.Platform.Android')

    if osWin:
        # xbmc.executebuiltin("System.Exec(cmd.exe /c start "+url+")")
        chrome_path = 'C:\Users\yugimaster\AppData\Local\Google\Chrome\Application\chrome.exe %s'
        webbrowser.get(using='google-chrome').open(url)
    elif osAndroid:
        xbmc.executebuiltin("StartAndroidActivity(com.android.chrome,,,"+url+")")
