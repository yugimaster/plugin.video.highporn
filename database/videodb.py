# -*- coding: utf-8 -*-

##################################################################################################
import logging
from videodb_functions import VideoDB_Functions

##################################################################################################
log = logging.getLogger("LD." + __name__)
##################################################################################################


class VideoDB():

    def __init__(self, cursor):

        self.cursor = cursor
        self.video_db = VideoDB_Functions(self.cursor)

    def get_videos(self):
        video_list = self.video_db.getVideos()
        return video_list

    def videos_add_update(self, item, date, time):
        video_item = self.video_db.getVideoItem_byName(item['title'])
        try:
            video_id = video_item[0]
        except Exception:
            video_id = self.create_entry_video()
        link_list = []
        for link in item['playlink']:
            link_list.append(link['playinfo'])
        self.video_db.replaceVideos(video_id,
                                    item['numberid'],
                                    item['title'],
                                    item['poster'],
                                    item['url'],
                                    item['plot'],
                                    "",
                                    ' / '.join(item['genre'].split('|')),
                                    "",
                                    ' / '.join(item['actors']),
                                    ' | '.join(link_list),
                                    date,
                                    time)

    def tag_add_update(self, tag):
        tag_item = self.video_db.getTagItem_byName(tag)
        try:
            tag_id = tag_item[0]
        except Exception:
            tag_id = self.create_entry_tag()
        self.video_db.replaceTag(tag_id, tag, "")

    def actor_add_update(self, actor, numberid):
        actor_item = self.video_db.getActorItem_byName(actor)
        try:
            actor_id = actor_item[0]
        except Exception:
            actor_id = self.create_entry_actor()
        self.video_db.replaceActor(actor_id, actor, "", "")
        self.video_db.replaceActorLink(actor_id, numberid, actor)

    def number_list_add_update(self, numberid):
        number_list_item = self.video_db.getNumberListItem_byNumId(numberid)
        try:
            number_list_id = number_list_item[0]
        except Exception:
            number_list_id = self.create_entry_number_list()
        if numberid:
            self.video_db.replaceNumberList(number_list_id, numberid, "", "")

    def create_entry_video(self):
        self.cursor.execute("select coalesce(max(video_id),0) from videos")
        video_id = self.cursor.fetchone()[0] + 1
        return video_id

    def create_entry_tag(self):
        self.cursor.execute("select coalesce(max(tag_id),0) from tag")
        tag_id = self.cursor.fetchone()[0] + 1
        return tag_id

    def create_entry_actor(self):
        self.cursor.execute("select coalesce(max(actor_id),0) from actor")
        actor_id = self.cursor.fetchone()[0] + 1
        return actor_id

    def create_entry_number_list(self):
        self.cursor.execute("select coalesce(max(id),0) from number_list")
        number_list_id = self.cursor.fetchone()[0] + 1
        return number_list_id
