# -*- coding: utf-8 -*-

#################################################################################################

import logging
from sqlite3 import OperationalError

##################################################################################################

log = logging.getLogger("LD." + __name__)

##################################################################################################


class VideoDB_Functions():

    def verify_cards_database(self):
        # Create the tables for the cards database
        # videos, tag, director, director_link, actor, actor_link, number_list
        self.videodb_cursor.execute("""CREATE TABLE IF NOT EXISTS videos(
            video_id INTEGER PRIMARY KEY,
            number_id VARCHAR(255),
            name TEXT,
            poster TEXT,
            url TEXT,
            description TEXT,
            descripttion_japan TEXT,
            categories TEXT,
            director TEXT,
            actors TEXT,
            scene TEXT,
            added_date TEXT,
            added_time INTEGER)""")
        self.videodb_cursor.execute("""CREATE TABLE IF NOT EXISTS tag(
            tag_id INTEGER PRIMARY KEY,
            name TEXT,
            hiragana TEXT)""")
        self.videodb_cursor.execute("""CREATE TABLE IF NOT EXISTS director(
            director_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            hiragana TEXT,
            art_urls TEXT)""")
        self.videodb_cursor.execute("""CREATE TABLE IF NOT EXISTS director_link(
            id INTEGER REFERENCES director(director_id),
            media_id INTEGER REFERENCES videos(video_id),
            name TEXT NOT NULL)""")
        self.videodb_cursor.execute("""CREATE TABLE IF NOT EXISTS actor(
            actor_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            chinese_name TEXT,
            hiragana TEXT,
            art_urls TEXT,
            description TEXT,
            desc_wiki TEXT)""")
        self.videodb_cursor.execute("""CREATE TABLE IF NOT EXISTS actor_link(
            id INTEGER,
            media_id INTEGER,
            name TEXT NOT NULL)""")
        self.videodb_cursor.execute("""CREATE TABLE IF NOT EXISTS number_list(
            id INTEGER PRIMARY KEY,
            number_id VARCHAR(255) REFERENCES videos(number_id),
            maker TEXT,
            publisher TEXT)""")

    def __init__(self, carddb_cursor):

        self.videodb_cursor = carddb_cursor
        self.verify_cards_database()

    def getVideos(self):
        videos = []
        query = ' '.join((
            "SELECT number_id, name, poster, url, description, added_date, added_time",
            "FROM videos"
        ))
        self.videodb_cursor.execute(query)
        rows = self.videodb_cursor.fetchall()
        for row in rows:
            listitem = {"number_id": row[0],
                        "name": row[1],
                        "poster": row[2],
                        "url": row[3],
                        "description": row[4],
                        "added_date": row[5],
                        "added_time": row[6]}
            videos.append(listitem)
        return videos

    def getVideo_byNameOrderASC(self):
        videos = []
        query = ' '.join((
            "SELECT *",
            "FROM videos ORDER BY name ASC"
        ))
        self.videodb_cursor.execute(query)
        rows = self.videodb_cursor.fetchall()
        for row in rows:
            listitem = {"number_id": row[1],
                        "name": row[2],
                        "poster": row[3],
                        "url": row[4],
                        "description": row[5],
                        "desc_japan": row[6],
                        "added_date": row[11],
                        "added_time": row[12]}
            videos.append(listitem)
        return videos

    def getVideo_byNameLike(self, name):
        keyword = "%" + name + "%"
        videos = []
        query = ' '.join((
            "SELECT *",
            "FROM videos",
            "WHERE name LIKE ?"
        ))
        self.videodb_cursor.execute(query, (keyword,))
        rows = self.videodb_cursor.fetchall()
        for row in rows:
            listitem = {"number_id": row[1],
                        "name": row[2],
                        "poster": row[3],
                        "url": row[4],
                        "description": row[5],
                        "desc_japan": row[6],
                        "added_date": row[11],
                        "added_time": row[12]}
            videos.append(listitem)
        return videos

    def getVideo_byAddedDate(self):
        videos = []
        query = ' '.join((
            "SELECT *",
            "FROM videos ORDER BY added_time DESC",
            "LIMIT 25"
        ))
        self.videodb_cursor.execute(query)
        rows = self.videodb_cursor.fetchall()
        for row in rows:
            listitem = {"number_id": row[1],
                        "name": row[2],
                        "poster": row[3],
                        "url": row[4],
                        "description": row[5],
                        "desc_japan": row[6],
                        "added_date": row[11],
                        "added_time": row[12]}
            videos.append(listitem)
        return videos

    def getGenre_byNameOrderASC(self):
        genres = []
        query = ' '.join((
            "SELECT *",
            "FROM tag ORDER BY name ASC"
        ))
        self.videodb_cursor.execute(query)
        rows = self.videodb_cursor.fetchall()
        for row in rows:
            genre = row[1]
            genres.append(genre)
        return genres

    def getActor_byNameOrderASC(self):
        query = ' '.join((
            "SELECT *",
            "FROM actor ORDER BY name ASC"
        ))
        try:
            self.videodb_cursor.execute(query)
            actors = self.videodb_cursor.fetchall()
            return actors
        except Exception:
            return None

    def getVideoItem_byName(self, name):
        query = ' '.join((
            "SELECT video_id, number_id, poster, url, description, descripttion_japan, categories, director, actors, scene",
            "FROM videos",
            "WHERE name = ?"
        ))
        try:
            self.videodb_cursor.execute(query, (name,))
            item = self.videodb_cursor.fetchone()
            return item
        except Exception:
            return None

    def getTagItem_byName(self, name):
        query = ' '.join((
            "SELECT tag_id, hiragana",
            "FROM tag",
            "WHERE name = ?"
        ))
        try:
            self.videodb_cursor.execute(query, (name,))
            item = self.videodb_cursor.fetchone()
            return item
        except Exception:
            return None

    def getActorItem_byName(self, name):
        query = ' '.join((
            "SELECT actor_id, hiragana, art_urls",
            "FROM actor",
            "WHERE name = ?"
        ))
        try:
            self.videodb_cursor.execute(query, (name,))
            item = self.videodb_cursor.fetchone()
            return item
        except Exception:
            return None

    def getActorLinkList_byName(self, name):
        query = ' '.join((
            "SELECT media_id, name",
            "FROM actor_link",
            "WHERE name = ?"
        ))
        try:
            self.videodb_cursor.execute(query, (name,))
            link_list = self.videodb_cursor.fetchall()
            return link_list
        except Exception:
            return None

    def getNumberListItem_byNumId(self, numberid):
        query = ' '.join((
            "SELECT id, maker, publisher",
            "FROM number_list",
            "WHERE number_id = ?"
        ))
        try:
            self.videodb_cursor.execute(query, (numberid,))
            item = self.videodb_cursor.fetchone()
            return item
        except Exception:
            return None

    def replaceVideos(self, *args):
        query = (
            '''
            REPLACE INTO videos(
                video_id, number_id, name, poster, url, description, descripttion_japan, categories, director, actors, scene, added_date, added_time)

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
        )
        self.videodb_cursor.execute(query, (args))

    def replaceVideosTime(self, *args):
        query = (
            '''
            REPLACE INTO videos(added_date, added_time)

            VALUES (?, ?)
            '''
        )
        self.videodb_cursor.execute(query, (args))

    def replaceTag(self, *args):
        query = (
            '''
            REPLACE INTO tag(
                tag_id, name, hiragana)

            VALUES (?, ?, ?)
            '''
        )
        self.videodb_cursor.execute(query, (args))

    def replaceDirector(self, *args):
        query = (
            '''
            REPLACE INTO director(
                director_id, name, hiragana, art_urls)

            VALUES (?, ?, ?, ?)
            '''
        )
        self.videodb_cursor.execute(query, (args))

    def replaceDirectorLink(self, *args):
        query = (
            '''
            REPLACE INTO director_link(
                id, media_id, name)

            VALUES (?, ?, ?)
            '''
        )
        self.videodb_cursor.execute(query, (args))

    def replaceActor(self, *args):
        query = (
            '''
            REPLACE INTO actor(
                actor_id, name, hiragana, art_urls)

            VALUES (?, ?, ?, ?)
            '''
        )
        self.videodb_cursor.execute(query, (args))

    def replaceActorLink(self, *args):
        query = (
            '''
            REPLACE INTO actor_link(
                id, media_id, name)

            VALUES (?, ?, ?)
            '''
        )
        self.videodb_cursor.execute(query, (args))

    def replaceNumberList(self, *args):
        query = (
            '''
            REPLACE INTO number_list(
                id, number_id, maker, publisher)

            VALUES (?, ?, ?, ?)
            '''
        )
        self.videodb_cursor.execute(query, (args))
