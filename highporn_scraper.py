# -*- coding: utf8 -*-

import os
import sys
import json
import sqlite3

sys.path.append(os.path.join('resources', 'lib'))
sys.path.append(os.path.join('database'))
from highporn import *
from xcity import *
from common import *
from videodb import VideoDB
from videodb_functions import VideoDB_Functions


HighPorn = HighPorn()
Xcity = Xcity()
DB_FILE = "highporn.db"
HOST = "http://highporn.net"


def get_all_videos(page):
    soup = HighPorn.videos(page)
    if not soup:
        return None
    div_videos = soup.find_all("div", {"class": "col-sm-6 col-md-4 col-lg-4"})
    if not div_videos:
        return None
    result = {}
    video_list = []
    for (count, divs) in enumerate(div_videos):
        detail_link = divs.find('a').get('href')
        img_url = divs.find('img').get('src')
        image = "http:" + img_url if img_url[:4] != "http" else img_url
        title = divs.find('span').get_text()
        detail = get_video_detail(detail_link, title)
        listitem = {"title": detail['title'],
                    "number_id": detail['number_id'],
                    "type": detail['type'],
                    "plot": detail['plot'],
                    "image": image,
                    "detail_url": HOST + detail_link,
                    "genres": detail['genres'],
                    "actors": detail['actors'],
                    "playlink": detail['playlink']}
        video_list.append(listitem)
        saveVideoDB(listitem)
        print "get video successfully:    " + str(count + 1) + " / " + str(len(div_videos))
    result['videos'] = video_list
    return result


def get_video_detail(detail_link, title):
    soup = HighPorn.detail(detail_link)
    if not soup:
        return None
    result = {}
    actors = []
    playurls = []
    meta_type = soup.find("meta", {"property": "og:type"})
    meta_actors = soup.find_all("meta", {"property": "video:actor"})
    meta_keywords = soup.find("meta", {"name": "keywords"})
    div_playlist = soup.find("div", {"id": "playlist"})
    playlist = div_playlist.find_all("span", {"class": "playlist_scene"})
    keywords = meta_keywords.get('content')
    number_id, name = get_video_number_id(title)
    for (count, meta) in enumerate(meta_actors):
        actor = meta.get('content')
        if not actor:
            continue
        actors.append(actor)
        actor_url, desc = get_actor_result(actor)
        saveActorDB(actor, actor_url, desc)
    if number_id != "none":
        saveNumberIdDB(number_id)
    for tag in keywords.split(', '):
        saveTagDB(tag)
    for item in playlist:
        playinfo = item.get('data-src')
        if not playinfo:
            continue
        play_title = item.get_text()
        listitem = {"name": name + " - " + play_title, "playinfo": playinfo}
        playurls.append(listitem)

    result['title'] = name
    result['number_id'] = number_id
    result['type'] = meta_type.get('content')
    result['plot'] = name
    result['genres'] = ' / '.join(keywords.split(', '))
    result['actors'] = actors
    result['playlink'] = playurls
    return result


def get_video_number_id(title):
    number_id = "none"
    title = title.strip()
    if "-" in title:
        str1 = title.split(' ')[0]
        words = str1.split('-')[1]
        if words.isdigit():
            number_id = str1
    if number_id == "none":
        name = title
    else:
        name = title[len(number_id) + 1:]
    return number_id, name


def save_to_local(page):
    if not os.path.exists(DB_FILE):
        create_connection()
    get_all_videos(page)


def create_connection():
    """
    create a database connection to a SQLite database
    """
    try:
        conn = sqlite3.connect(DB_FILE, 120)
        cursor = conn.cursor()
        VideoDB_Functions(cursor)
    except Exception:
        print_exc()
    finally:
        conn.close()


def saveVideoDB(item):
    with sqlite3.connect(DB_FILE, 120) as videos_conn:
        cursor = videos_conn.cursor()
        vo = VideoDB(cursor)
        date = GetDateTimeString()
        vo.videos_main_add_update(item, date, int(time.time()))
        videos_conn.commit()
        cursor.close()


def saveActorDB(actor, url, desc):
    with sqlite3.connect(DB_FILE, 120) as actor_conn:
        cursor = actor_conn.cursor()
        ac = VideoDB(cursor)
        ac.actor_add_update(actor, url, desc)
        actor_conn.commit()
        cursor.close()


def saveNumberIdDB(number_id):
    with sqlite3.connect(DB_FILE, 120) as numberid_conn:
        cursor = numberid_conn.cursor()
        nu = VideoDB(cursor)
        nu.number_list_add_update(number_id)
        numberid_conn.commit()
        cursor.close()


def saveTagDB(tag):
    with sqlite3.connect(DB_FILE, 120) as tag_conn:
        cursor = tag_conn.cursor()
        ta = VideoDB(cursor)
        ta.tag_add_update(tag)
        tag_conn.commit()
        cursor.close()


def translator():
    from googletrans import Translator
    translator = Translator()
    print translator.translate('Mizuno Asahi', dest='la')


def get_actor_result(keyword):
    soup = Xcity.search(keyword)
    if not soup:
        return None
    try:
        p_tn = soup.find("p", {"class": "tn"})
        detail_link = p_tn.find("a").get("href")
        image_url = p_tn.find("img").get("src")
        detail_url = "https://xxx.xcity.jp/idol/" + detail_link
        image = "https:" + image_url if image_url[:4] != "http" else image_url
    except Exception:
        print "Can't find " + keyword + " result"
        image = "https://xcity.jp/imgsrc/wp-content/themes/xcity-ja/img/noimage.gif?width=200&height=200"
        detail_url = ""
    actor_desc = get_actor_description(detail_url)
    return image, actor_desc


def get_actor_description(detail_url):
    if not detail_url:
        return ""
    soup = Xcity.detail(detail_url)
    if not soup:
        return None
    try:
        dl_profile = soup.find("dl", {"class": "profile"})
        dd_list = dl_profile.find_all("dd")
        textbox = []
        for dd in dd_list[1:]:
            span_text = dd.find("span").get_text()
            text = span_text + ":  " + dd.get_text()[len(span_text):]
            textbox.append(text)
        desc = '. '.join(textbox)
    except Exception:
        print_exc()
        desc = ""
    return desc


if __name__ == '__main__':
    save_to_local(15)
    # translator()
    # s, t = get_actor_result("Asahi Mizuno")
    # print s
    # print t
