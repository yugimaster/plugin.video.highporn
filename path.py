# -*- coding: utf8 -*-

from kodiswift import Plugin, CLI_MODE, xbmcaddon, ListItem, xbmc, xbmcgui, xbmcplugin
import os
import sys
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
from highporn import *
from common import *


plugin = Plugin()
HighPorn = HighPorn()
# PAGE_ROWS = plugin.get_setting("page_rows")
# SEASON_CACHE = plugin.get_storage('season')
# HISTORY = plugin.get_storage('history')


# def set_auto_play():
#     auto_play_setting = plugin.get_setting("auto_next")
#     print setSettingByRPC("videoplayer.autoplaynextitem", auto_play_setting)

print sys.argv


# main entrance
@plugin.route('/')
def index():
    data = HighPorn.index()
    item = ListItem.from_dict(**{
        'label': colorize("Input Keyword", "yellow"),
        'icon': ADDON_PATH + "/resources/media/search.png",
        'path': plugin.url_for("input_keyword"),
        'is_playable': False
    })
    yield item
    item = ListItem.from_dict(**{
        'label': colorize("History List", "yellow"),
        'icon': ADDON_PATH + "/resources/media/history.png",
        'path': "",
        'is_playable': False
    })
    yield item
    for item in data:
        link = item.find('a').get('href')
        img_url = item.find('img').get('src')
        img = "http:" + img_url if img_url[:4] != "http" else img_url
        title = item.find('img').get('title')
        listitem = ListItem.from_dict(**{
            'label': title,
            'icon': img,
            'fanart': img,
            'path': plugin.url_for("movie_detail", url_link=link),
            'is_playable': False
        })
        yield listitem


# search entrance
# @plugin.route('/hotword/')
# def hotword():
#     yield {
#             'label': colorize("输入关键字搜索", "yellow"),
#             'path': plugin.url_for("input_keyword"),
#             'is_playable': False
#         }
#     hotwords = Bigmovie.hot_word()
#     for word in hotwords["data"]["wordList"]:
#         word = word.encode("utf8")
#         item = {
#             'label': colorize(word, "green"),
#             'path': plugin.url_for("search", title=word),
#             'is_playable': False
#         }
#         yield item


# get search result by input keyword
@plugin.route("/input/")
def input_keyword():
    keyboard = Keyboard('', 'Please Input Keyword')
    xbmc.sleep(1500)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        keyword = keyboard.getText()
        url = plugin.url_for("search", keyword=keyword)
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
            'fanart': img,
            'path': plugin.url_for("movie_detail", url_link=link),
            'is_playable': False
        })
        yield item


# @plugin.route('/movie_list/<method>/')
# def movie_list(method):
#     if method not in ["hot", "new", "all"]:
#         return
#     if method in ["hot", "new"]:
#         r_method = "new_hot"
#     else:
#         r_method = "all"
#     detail = Bigmovie.movie_list(r_method)
#     for movie in detail[method + "list"]:
#         item = ListItem.from_dict(**{
#             'label': movie.get("title"),
#             'path': plugin.url_for("detail", movie_id=movie.get("id", "")),
#             'thumbnail': movie.get("img"),
#             'poster': movie.get("img"),
#             'is_playable': True
#         })
#         print movie.get("title").encode("utf8")
#         if r_method == "all":
#             with open("C:\\xbmc-workspace\\LocalDB\\Movies\\" + movie.get("title").replace("/", " ") + ".strm", "w+") as f:
#                 f.write(plugin.url_for("detail", movie_id=movie.get("id", "")))
#         yield item


# @plugin.route('/tv_list/<method>/')
# def tv_list(method):
#     if method not in ["hot", "new", "all"]:
#         return
#     if method in ["hot", "new"]:
#         r_method = "new_hot"
#     else:
#         r_method = "all"
#     detail = Bigmovie.tv_list(r_method)
#     for tvshow in detail[method + "list"]:
#         item = ListItem.from_dict(**{
#             'label': tvshow["title"],
#             'path': plugin.url_for("episode_list", tv_id=tvshow.get("id", "")),
#             'icon': tvshow["img"],
#             'thumbnail': tvshow["img"],
#             'poster': tvshow["img"],
#             'is_playable': False
#         })
#         yield item


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
        'icon': data['poster'],
        'path': plugin.url_for("episode_list", url_link=url_link),
        'fanart': data['poster']
    })
    yield ListItem.from_dict(**{
        'label': colorize("Actors", "green"),
        'icon': ADDON_PATH + "/resources/media/actors.png",
        'path': plugin.url_for("actor_list", actors=actor_str),
    })
    yield ListItem.from_dict(**{
        'label': colorize("Categories", "green"),
        'icon': ADDON_PATH + "/resources/media/category.png",
        'path': plugin.url_for("category_list", category=data['genre']),
    })


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
            'path': plugin.url_for("search", keyword=item)
        }
        yield listitem


@plugin.route('/category_list/<category>/')
def category_list(category):
    listitems = category.split("|")
    for item in listitems:
        listitem = {
            'label': item,
            'icon': ADDON_PATH + "/resources/media/category.png",
            'path': plugin.url_for("search", keyword=item)
        }
        yield listitem


# def add_history(seasonId, index, Esid, title):
#     if "list" not in HISTORY:
#         HISTORY["list"] = []
#     for l in HISTORY["list"]:
#         if l["seasonId"] == seasonId:
#             HISTORY["list"].remove(l)
#     item = {"seasonId": seasonId,
#             "index": index,
#             "sid": Esid,
#             "season_name": title}
#     HISTORY["list"].insert(0, item)


# @plugin.route('/history/list/')
# def list_history():
#     if "list" in HISTORY:
#         for l in HISTORY["list"]:
#             seasonId = l["seasonId"]
#             index = l["index"]
#             sid = l["sid"]
#             yield {
#                 'label': u"[COLOR green]{title}[/COLOR]  观看到第[COLOR yellow]{index}[/COLOR]集".format(title=l["season_name"], index=l["index"]),
#                 'path': plugin.url_for("detail", seasonId=seasonId),
#                 'is_playable': False
#             }


def get_movie_detail_json(detail):
    if not detail:
        return None
    result = {}
    actors = []
    meta_title = detail.find("meta", {"property": "og:title"})
    meta_image = detail.find("meta", {"property": "og:image"})
    meta_type = detail.find("meta", {"property": "og:type"})
    meta_description = detail.find("meta", {"property": "og:description"})
    meta_actors = detail.find_all("meta", {"property": "video:actor"})
    meta_keywords = detail.find("meta", {"name": "keywords"})
    keywords = meta_keywords.get('content')
    image_url = meta_image.get('content')
    image = "http:" + image_url if image_url[:4] != "http" else image_url
    for (count, item) in enumerate(meta_actors):
        actor = item.get('content')
        actors.append(actor)

    result['title'] = meta_title.get('content')
    result['poster'] = image
    result['type'] = meta_type.get('content')
    result['plot'] = meta_description.get('content')
    result['genre'] = '|'.join(keywords.split(', '))
    result['actors'] = actors
    import json
    print json.dumps(result)
    return result


def save_to_local():
    # save file to strm
    pass
    # insert into db