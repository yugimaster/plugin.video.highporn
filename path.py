# -*- coding: utf8 -*-

from kodiswift import Plugin, CLI_MODE, xbmcaddon, ListItem, xbmc, xbmcgui, xbmcplugin
import os
import sys
import json
import sqlite3
import time
try:
    from ChineseKeyboard import Keyboard
except Exception, e:
    print e
    from xbmc import Keyboard

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_DATA_PATH = xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID).decode("utf-8")
sys.path.append(os.path.join(ADDON_PATH, 'resources', 'lib'))
sys.path.append(os.path.join(ADDON_PATH, 'database'))
from highporn import *
from common import *
from videodb import VideoDB
from videodb_functions import VideoDB_Functions


plugin = Plugin()
HighPorn = HighPorn()
DB_FILE = ADDON_PATH + "/database/japanmovies.db"


print sys.argv


# main entrance
@plugin.route('/')
def index():
    if not os.path.exists(DB_FILE):
        create_connection()
    item = ListItem.from_dict(**{
        'label': colorize("Input Keyword", "yellow"),
        'icon': ADDON_PATH + "/resources/media/search.png",
        'path': plugin.url_for("input_keyword"),
        'is_playable': False
    })
    yield item
    item = ListItem.from_dict(**{
        'label': colorize("Video List Library", "yellow"),
        'icon': ADDON_PATH + "/resources/media/library.png",
        'path': plugin.url_for("movie_library"),
        'is_playable': False
    })
    yield item


# get search result by input keyword
@plugin.route("/input/")
def input_keyword():
    keyboard = Keyboard('', 'Please Input Keyword')
    xbmc.sleep(1500)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        keyword = keyboard.getText()
        url = plugin.url_for("movie_list", params=keyword)
        plugin.redirect(url)


@plugin.route('/search/<keyword>/')
def search(keyword):
    params = keyword.split("|")
    if not params:
        return
    if len(params) > 1:
        data = HighPorn.search(params[0], params[1])
    else:
        data = HighPorn.search(params[0])
    for item in data:
        link = item.find('a').get('href')
        img_url = item.find('img').get('src')
        img = "http:" + img_url if img_url[:4] != "http" else img_url
        title = item.find('img').get('title')
        item = ListItem.from_dict(**{
            'label': title,
            'icon': img,
            'path': plugin.url_for("movie_detail", url_link=link),
            'is_playable': False
        })
        yield item


@plugin.route('/movie_list/<params>/')
def movie_list(params):
    params = params.split("|")
    if len(params) > 1:
        html = HighPorn.search(params[0], params[1])
    else:
        html = HighPorn.search(params[0])
    data = get_search_result_json(html)
    if not data:
        return
    item = ListItem.from_dict(**{
        'label': colorize("Home", "yellow"),
        'icon': ADDON_PATH + "/resources/media/home.png",
        'path': plugin.url_for("index"),
        'is_playable': False
    })
    yield item
    for video in data['video_list']:
        item = ListItem.from_dict(**{
            'label': video['title'],
            'icon': video['image'],
            'path': plugin.url_for("movie_detail", url_link=video['link']),
            'is_playable': False
        })
        yield item
    for page in data['page_list']:
        item = ListItem.from_dict(**{
            'label': page['name'],
            'path': plugin.url_for("movie_list", params=page['keywords']),
            'is_playable': False
        })
        yield item


@plugin.route('/detail/<url_link>')
def movie_detail(url_link):
    detail = HighPorn.detail(url_link)
    data = get_movie_detail_json(detail)
    if not data:
        return
    actor_str = ""
    for (count, c) in enumerate(data['actors']):
        if count != len(data['actors']) - 1:
            actor_str = actor_str + c + "/"
        else:
            actor_str = actor_str + c
    yield {
        'label': "Playlist",
        'icon': ADDON_PATH + "/resources/media/playlist.png",
        'path': plugin.url_for("episode_list", url_link=url_link)
    }
    yield ListItem.from_dict(**{
        'label': "Poster",
        'icon': ADDON_PATH + "/resources/media/image.png",
        'path': plugin.url_for("image_fanart", img_url=data['poster'])
    })
    yield ListItem.from_dict(**{
        'label': "Actor",
        'icon': ADDON_PATH + "/resources/media/actors.png",
        'path': plugin.url_for("actor_list", actors=actor_str),
    })
    yield ListItem.from_dict(**{
        'label': "Categories",
        'icon': ADDON_PATH + "/resources/media/category.png",
        'path': plugin.url_for("category_list", category=data['genre']),
    })


@plugin.route('/image_fanart/<img_url>')
def image_fanart(img_url):
    window = xbmcgui.WindowDialog()
    window.setCoordinateResolution(0)
    bg = xbmcgui.ControlImage(0, 0, 1920, 1080, ADDON_PATH + "/resources/media/bg.png")
    window.addControl(bg)
    fanart = xbmcgui.ControlImage(0, 0, 1440, 900, img_url)
    fanart.setPosition((1920 - fanart.getWidth()) / 2, (1080 - fanart.getHeight()) / 2)
    window.addControl(fanart)
    window.show()
    window.doModal()


@plugin.route('/episode_list/<url_link>/')
def episode_list(url_link):
    detail = HighPorn.detail(url_link)
    playlist = detail.find("div", {"id": "playlist"})
    playurls = playlist.find_all("span", {"class": "playlist_scene"})
    for index, episode in enumerate(playurls):
        title = episode.get_text()
        playinfo = episode.get('data-src')
        url = ""
        if not playinfo:
            continue
        try:
            if playinfo[:4] != "http":
                url = HighPorn.playurl(playinfo)
            else:
                url = playinfo
        except Exception:
            print_exc()
        item = ListItem(**{
            'label': title,
            'path': url,
        })
        item.set_is_playable(True)
        yield item


@plugin.route('/actor_list/<actors>/')
def actor_list(actors):
    listitems = actors.split("/")
    for item in listitems:
        listitem = {
            'label': item,
            'icon': ADDON_PATH + "/resources/media/actors.png",
            'path': plugin.url_for("movie_list", params=item)
        }
        yield listitem


@plugin.route('/category_list/<category>/')
def category_list(category):
    listitems = category.split("|")
    for item in listitems:
        listitem = {
            'label': item,
            'icon': ADDON_PATH + "/resources/media/category.png",
            'path': plugin.url_for("movie_list", params=item)
        }
        yield listitem


@plugin.route('/history_list/')
def history_list():
    video_list = get_history_db()
    if not video_list:
        return
    for video in video_list:
        item = set_video_item(video)
        yield item


@plugin.route('/movie_library/')
def movie_library():
    yield {
        'label': "Genre",
        'icon': ADDON_PATH + "/resources/media/category.png",
        'path': plugin.url_for("genre_db"),
        'is_playable': False
    }
    yield {
        'label': "Title",
        'icon': ADDON_PATH + "/resources/media/title.png",
        'path': plugin.url_for("title_db"),
        'is_playable': False
    }
    yield {
        'label': "Actor",
        'icon': ADDON_PATH + "/resources/media/actors.png",
        'path': plugin.url_for("actor_db")
    }
    yield {
        'label': "Recently Added",
        'icon': ADDON_PATH + "/resources/media/recentlyadded.png",
        'path': plugin.url_for("added_list_db")
    }


@plugin.route('/genre_db/')
def genre_db():
    genre_list = get_genres_db()
    for item in genre_list:
        item = ListItem.from_dict(**{
            'label': item,
            'icon': ADDON_PATH + "/resources/media/tag.png",
            'path': plugin.url_for("movie_list", params=item),
            'is_playable': False
        })
        yield item


@plugin.route('/title_db/')
def title_db():
    yield {
        'label': "All Videos",
        'icon': ADDON_PATH + "/resources/media/videos.png",
        'path': plugin.url_for("video_list_db"),
        'is_playable': False
    }
    yield {
        'label': "Title Search",
        'icon': ADDON_PATH + "/resources/media/search.png",
        'path': plugin.url_for("input_title"),
        'is_playable': False
    }


@plugin.route('/actor_db/')
def actor_db():
    actor_list = get_actors_db()
    for actor in actor_list:
        if not actor:
            continue
        item = ListItem.from_dict(**{
            'label': actor[2] if actor[2] else actor[1],
            'label2': actor[2],
            'icon': actor[4] if actor[4] else ADDON_PATH + "/resources/media/actor.png",
            'path': plugin.url_for("movie_list", params=actor[1]),
            'is_playable': False
        })
        yield item


@plugin.route('/video_list_db/')
def video_list_db():
    video_list = get_videos_db()
    item = ListItem.from_dict(**{
        'label': colorize("Home", "yellow"),
        'icon': ADDON_PATH + "/resources/media/home.png",
        'path': plugin.url_for("index"),
        'is_playable': False
    })
    yield item
    for video in video_list:
        item = set_video_item(video)
        if not item:
            continue
        yield item


@plugin.route('/added_list_db/')
def added_list_db():
    video_list = get_recently_added_db()
    for video in video_list:
        item = set_video_item(video)
        if not item:
            continue
        yield item


# get search result by input title
@plugin.route("/title/")
def input_title():
    keyboard = Keyboard('', 'Please Input Title')
    xbmc.sleep(1500)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        keyword = keyboard.getText()
        if keyword:
            video_list = get_title_search_db(keyword)
            for video in video_list:
                item = set_video_item(video)
                yield item


def get_movie_detail_json(detail):
    if not detail:
        return None
    result = {}
    actors = []
    playurls = []
    meta_title = detail.find("meta", {"property": "og:title"})
    meta_image = detail.find("meta", {"property": "og:image"})
    meta_type = detail.find("meta", {"property": "og:type"})
    meta_url = detail.find("meta", {"property": "og:url"})
    meta_description = detail.find("meta", {"property": "og:description"})
    meta_actors = detail.find_all("meta", {"property": "video:actor"})
    meta_keywords = detail.find("meta", {"name": "keywords"})
    div_playlist = detail.find("div", {"id": "playlist"})
    playlist = div_playlist.find_all("span", {"class": "playlist_scene"})
    keywords = meta_keywords.get('content')
    image_url = meta_image.get('content')
    image = "http:" + image_url if image_url[:4] != "http" else image_url
    for (count, item) in enumerate(meta_actors):
        actor = item.get('content')
        actors.append(actor)
    for episode in playlist:
        playinfo = episode.get('data-src')
        if not playinfo:
            continue
        title = episode.get_text()
        listitem = {"name": title, "playinfo": playinfo}
        playurls.append(listitem)

    result['title'] = meta_title.get('content')
    result['numberid'] = get_movie_number_id(result['title'])
    result['poster'] = image
    result['type'] = meta_type.get('content')
    result['plot'] = meta_description.get('content')
    result['genre'] = '|'.join(keywords.split(', '))
    result['actors'] = actors
    result['url'] = meta_url.get('content')
    result['playlink'] = playurls
    add_history_db(result)
    return result


def get_search_result_json(data):
    if not data:
        return None
    result = {}
    video_list = []
    page_list = []
    div_videolist = data.find_all("div", {"class": "col-sm-6 col-md-4 col-lg-4"})
    if not div_videolist:
        return None
    ul_page = data.find("ul", {"class": "pagination pagination-lg"})
    if ul_page:
        a_page = ul_page.find_all('a')
    else:
        a_page = []
    for item in div_videolist:
        link = item.find('a').get('href')
        img_url = item.find('img').get('src')
        img = "http:" + img_url if img_url[:4] != "http" else img_url
        title = item.find('img').get('title')
        listitem = {"title": title, "image": img, "link": link}
        video_list.append(listitem)
    for a in a_page:
        link = a.get('href')
        page_name = a.get_text()
        params = link.split('?')[1]
        param1 = params.split('&')[0]
        param2 = params.split('&')[1]
        keywords = param1.split('=')[1] + "|" + param2.split('=')[1]
        item = {"url": link, "keywords": keywords, "name": page_name}
        page_list.append(item)
    result['video_list'] = video_list
    result['page_list'] = page_list
    return result


def get_history_json():
    with open(ADDON_PATH + "/history.json", "r") as f:
        load_dict = json.load(f)
        f.close()
        return load_dict


def get_history_db():
    with sqlite3.connect(DB_FILE, 120) as videos_conn:
        cursor = videos_conn.cursor()
        vo = VideoDB(cursor)
        video_list = vo.get_videos()
        videos_conn.commit()
        cursor.close()
        return video_list


def get_genres_db():
    with sqlite3.connect(DB_FILE, 120) as genres_conn:
        cursor = genres_conn.cursor()
        ge = VideoDB(cursor)
        genre_list = ge.get_genres_asc()
        genres_conn.commit()
        cursor.close()
        return genre_list


def get_videos_db():
    with sqlite3.connect(DB_FILE, 120) as videos_conn:
        cursor = videos_conn.cursor()
        vo = VideoDB(cursor)
        video_list = vo.get_videos_asc()
        videos_conn.commit()
        cursor.close()
        return video_list


def get_recently_added_db():
    with sqlite3.connect(DB_FILE, 120) as videos_conn:
        cursor = videos_conn.cursor()
        vo = VideoDB(cursor)
        video_list = vo.get_videos_added()
        videos_conn.commit()
        cursor.close()
        return video_list


def get_actors_db():
    with sqlite3.connect(DB_FILE, 120) as actors_conn:
        cursor = actors_conn.cursor()
        ac = VideoDB(cursor)
        actor_list = ac.get_actors_asc()
        actors_conn.commit()
        cursor.close()
        return actor_list


def get_title_search_db(title):
    with sqlite3.connect(DB_FILE, 120) as videos_conn:
        cursor = videos_conn.cursor()
        vo = VideoDB(cursor)
        video_list = vo.get_videos_title_search(title)
        videos_conn.commit()
        cursor.close()
        return video_list


def set_video_item(item):
    if not item['url']:
        return None
    listitem = ListItem.from_dict(**{
        'label': item['desc_japan'] if item['desc_japan'] else item['name'],
        'icon': item['poster'],
        'path': plugin.url_for("movie_detail", url_link=item['url'][19:]),
        'is_playable': False
    })
    return listitem


def get_movie_number_id(title):
    number_id = ""
    if "-" in title:
        str1 = title.split(' ')[0]
        if not str1:
            return number_id
        words = str1.split('-')[1]
        if words.isdigit():
            number_id = str1
    return number_id


@run_async
def add_history(result):
    json_history = get_history_json()
    video_list = json_history['videos']
    total = json_history['total']
    item = {"title": result['title'],
            "numberid": result['numberid'],
            "poster": result['poster'],
            "plot": result['plot'],
            "genre": result['genre'],
            "actors": result['actors'],
            "url": result['url'],
            "playlink": result['playlink']}
    if not video_list:
        json_history['videos'].append(item)
        json_history['total'] = total + 1
    else:
        for video in video_list:
            if video['title'] == result['title']:
                json_history['videos'].remove(video)
                total -= 1
                break
        json_history['videos'].insert(0, item)
        json_history['total'] = total + 1
    with open(ADDON_PATH + "/history.json", "w") as f:
        json.dump(json_history, f)
        print "add history successfully"
        f.close()


@run_async
def add_history_db(result):
    if not result:
        return
    saveVideoDB(result)
    uploadTagListDB(result['genre'])
    uploadActorListDB(result['actors'], result['numberid'])
    saveNumberIdDB(result['numberid'])


def save_to_local():
    if not os.path.exists(DB_FILE):
        create_connection()
    json_history = get_history_json()
    video_list = json_history['videos']
    for item in video_list:
        saveVideoDB(item)
        uploadTagListDB(item['genre'])
        uploadActorListDB(item['actors'], item['numberid'])
        saveNumberIdDB(item['numberid'])


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
        vo.videos_add_update(item, date, int(time.time()))
        videos_conn.commit()
        cursor.close()


def saveTagDB(tag):
    with sqlite3.connect(DB_FILE, 120) as tag_conn:
        cursor = tag_conn.cursor()
        ta = VideoDB(cursor)
        ta.tag_add_update(tag)
        tag_conn.commit()
        cursor.close()


def saveActorDB(actor, numberid):
    with sqlite3.connect(DB_FILE, 120) as actor_conn:
        cursor = actor_conn.cursor()
        ac = VideoDB(cursor)
        ac.actor_add_update(actor, numberid)
        actor_conn.commit()
        cursor.close()


def saveNumberIdDB(numberid):
    with sqlite3.connect(DB_FILE, 120) as numberid_conn:
        cursor = numberid_conn.cursor()
        nu = VideoDB(cursor)
        nu.number_list_add_update(numberid)
        numberid_conn.commit()
        cursor.close()


def uploadTagListDB(tags):
    tag_list = tags.split('|')
    for tag in tag_list:
        saveTagDB(tag)


def uploadActorListDB(actors, numberid):
    for actor in actors:
        saveActorDB(actor, numberid)
