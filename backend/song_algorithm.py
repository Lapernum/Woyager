import numpy as np
import sys
import os
# sys.path.insert(0, "Data")
# TODO: change to the dir to your
sys.path.append(os.path.join("D:/GATECH/TreeMusicRecommendation"))
from Data.data_api import *
from datetime import datetime
import math
import pdb
import random
# import operator

random.seed(6242)

class SelfListening:
    def __init__(self, user='rj'):
        # print(os.path.join("Data/conf.json"))
        self.dbapi = database_api(os.path.join("Data/conf.json"))
        self.lastapi = lastfm_api(os.path.join("Data/conf.json"))

        # The top tracks of the user, 
        # list(dict(track_name, track_id, track_url, track_listening_count, artist_id))
        self.top_track = self.lastapi.get_top_tracks(user)

        # The recent tracks listened by the user, 
        # list(dict(track_name, track_url, listened_at, artist_id))
        self.recent = self.lastapi.get_recent_tracks(user, page_limit=1)
        
        # A list that records tuple(track_name, artist_name). 
        # This records the track recently listened by the user and the tracks added by the user
        self.visited = list()
        # The top artists of the user, list(artist_id)
        # currently, list(dict(artist_id, artist_name, count))
        self.top_artist = self.lastapi.get_top_artist(user)

        # For target selection
        self.target_artist = sorted(self.top_artist, key=lambda x: x['artist_listening_count'], reverse=True)
        self.target_artist = self.target_artist[:4]
        self.target_artist = {i['artist_name']: i['artist_listening_count'] for i in self.target_artist}
        # The added tracks that is selected by user in the process, list(track_id)
        self.added_track = list()
        self.added_track_tag = {}
        # The selected tracks from select_songs()
        self.selected = list()
        # The similarity between a track and the group of tracks listened previously by user.
        # As a dict {track: score}
        # self.similarity = {}

        # Build two track tags cache dictionary
        self.top_track_tags = list()
        self.rec_track_tags = list()
        self.artist_tags = {}
        self.build_tag_dict()

        # The top tags from top_track and recent_track, dict(tag_name: count)
        self.top_tag = {}
        self.target_tag = {}
        self.build_top_tags()
        # The target tags and artists for frontend: {'tags': list(tags), 'artists': list(artists)}
        self.target = {'tag': list(self.target_tag.keys()), 'artist': list(self.target_artist.keys())}

        # Mode, depedent on the selected button
        self.mode = 'tag'
    
    # This will be an interactive function with front end
    def get_target(self):
        '''
        This function returns self.target
        '''
        return self.target

    # This will be an interactive function with front end
    def add_track(self, added_song):
        '''
        This function appends the added song selected in "Self-listening Mode" to added_track
        Along with the addition, this will also update self.visited and self.added_track_tag

        Input:
            - added_song: the {'track_name', 'artist_name'} dictionary of the added song
        
        Output:
            - None
        '''
        self.added_track.append(added_song)
        self.visited.append((added_song['track_name'], added_song['artist_name']))
        # Update self.added_track_tag for 'recurrent' idea
        track_tags = self.lastapi.get_track_tags(added_song['track_name'], added_song['artist_name'])
        if track_tags is not None:
            tag_dict = {t['tag_name']: t['tag_count'] for t in track_tags}
            for t, c in tag_dict.items():
                if t in self.added_track_tag:
                    self.added_track_tag[t] += c
                else:
                    self.added_track_tag[t] = c
        max_tag_cnt = max(d for d in self.added_track_tag.values())

        self.added_track_tag = {tag: math.floor((count / max_tag_cnt) * 100) for tag, count in self.added_track_tag.items()}

    # This will be an interactive function with front end
    def change_mode(self, pressed=None):
        '''
        Changes mode according to selected item in self.target

        Input:
            - mode: either 'tag' or 'artist',
            anythin else will be considered as 'tag'
        '''
        if pressed in self.target['artist']:
            self.mode = 'artist'
            self.select_songs(pressed)
        elif pressed in self.target['tag']:
            self.mode = 'tag'
            self.select_songs(pressed)
        else:
            raise KeyError("The selected item is neither an artist or a tag")

    def build_tag_dict(self):
        '''
        Build the 2 top_tag cache dict:
        1. Count the top tags of top tracks and recent tracks
        2. Store in self.top_track_tags and self.recent_track_tags
        Input:
            - None
        Output:
            - None: update self.top_track_tags and self.recent_track_tags dictionary
        '''
        print('Start cache building')
        idx = 0
        for track in self.top_track:
            idx += 1
            if idx > 50:
                break
            t_name = track['track_name']
            a_name = track['artist_name']
            # Some track does not have artist mbid, even though the artist name is present
            # if a_id == "":
            #     self.top_track_tags.append({})
            #     continue
            # a_name = self.lastapi.get_artist_name(a_id)

            # Some (t, a) combination does not return track tags
            # need to return an error code
            if a_name is not None:
                # if not error:
                track_tags = self.lastapi.get_track_tags(t_name, a_name)
                if track_tags is None or len(track_tags) == 0:
                    idx -= 1
                    continue
                tag_dict = {t['tag_name']: t['tag_count'] for t in track_tags}
                self.top_track_tags.append(tag_dict)
        print("Top track tags cache built")
        idx = 0
        for track in self.recent:
            idx += 1
            if idx > 20:
                break
            t_name = track['track_name']
            a_name = track['artist_name']
            
            # Some track does not have artist mbid, even though the artist name is present
            if a_name is not None:
                self.visited.append((t_name, a_name))
                track_tags = self.lastapi.get_track_tags(t_name, a_name)
                if track_tags is None or len(track_tags) == 0:
                    idx -= 1
                    continue
                tag_dict = {t['tag_name']: t['tag_count'] for t in track_tags}
                self.rec_track_tags.append(tag_dict)
        print("Recent track tags cache built")
        idx = 0 
        for artist in self.top_artist:
            idx += 1
            if idx > 20:
                break
            artist_name = artist['artist_name']
            count = artist['artist_listening_count']
            
            if artist_name in self.artist_tags:
                continue
            else:
                tags = self.lastapi.get_artist_tags(artist_name)
                tag_dict = {t['tag_name']: t['tag_count'] for t in tags}
                self.artist_tags[artist_name] = tag_dict
        print("Artist tag cache built")

    def build_top_tags(self):
        '''
        Build the top_tag dict:
        1. For top tracks, use tag_count * log(listened count)
        2. For recent tracks, use tag_count * exp(time_diff * decay)
        3. For top artists, use tag_count * log(listened count)
        4. Currently, assign proportion to be 0.6 top track, 0.4 recent track
        5. Normalize, so the top 1 tag has value 100.
        Input:
            - None: require top_track, recent, top_track_tags, rec_track_tags,
                    and top_artist
        Output:
            - None: update self.top_tag dict
        '''
        for i in range(len(self.top_track_tags)):
            if i > 50:
                break
            listened_count = self.top_track[i]['track_listening_count']
            tags = self.top_track_tags[i]
            for t, c in tags.items():
                # pdb.set_trace()
                if t in self.top_tag:
                    self.top_tag[t] += c * np.log(listened_count) * 0.6
                else:
                    self.top_tag[t] = c * np.log(listened_count) * 0.6
        print("Add top_track_tags to top_tags")
        now = datetime.now()
        for i in range(len(self.rec_track_tags)):
            if i > 20:
                break
            timestamp = self.recent[i]['listened_at']
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            timediff = (now - timestamp).total_seconds()
            weight = np.exp(-0.01 * timediff)
            tags = self.rec_track_tags[i]
            for t, c in tags.items():
                if t in self.top_tag:
                    self.top_tag[t] += c * weight * 0.4
                else:
                    self.top_tag[t] = c * weight * 0.4
        print("Add rec_track_tags to top_tags")
        idx = 0
        for artist in self.top_artist:
            idx += 1
            if idx > 20:
                break
            # Assume {tag: count} dict structure
            artist_name = artist['artist_name']
            count = artist['artist_listening_count']
            
            artist_tags = self.artist_tags[artist_name]
            for tag, cnt in artist_tags.items():
                
                if tag in self.top_tag:
                    self.top_tag[tag] += np.log(count) * cnt
            
        print("Add top_artist_tags to top_tags")
        # pdb.set_trace()
        max_tag_cnt = max(d for d in self.top_tag.values())
        temp = sorted(self.top_tag.items(), key=lambda x: x[1], reverse=True)
        self.top_tag = dict(temp[:30])
        self.target_tag = dict(temp[:8])

        self.top_tag = {tag: math.floor((count / max_tag_cnt) * 100) for tag, count in self.top_tag.items()}
        self.target_tag = {tag: math.floor((count / max_tag_cnt) * 100) for tag, count in self.target_tag.items()}

    def tag_sim_score(self, tag_dict1=None, tag_dict2=None):
        '''
        This function calculates the similarity score between two dictionary of tags.
        
        Input:
            - tag_dict1: a {tag: count} pair dictionary
            - tag_dict2: a {tag: count} pair dictionary

        Output:
            - score: a float number representing similarity
        '''
        if len(tag_dict1) == 0 or len(tag_dict2) == 0:
            return 0.0
        all_keys = set(tag_dict1.keys()) | set(tag_dict2.keys())
        
        # print(all_keys)
        t1 = np.zeros(len(all_keys))
        t2 = np.zeros(len(all_keys))
        for i, key in enumerate(all_keys):
            if key in tag_dict1:
                t1[i] = tag_dict1[key]
            if key in tag_dict2:
                t2[i] = tag_dict2[key]
        prod = np.dot(t1, t2)
        norm1 = np.linalg.norm(t1)
        norm2 = np.linalg.norm(t2)
        
        return prod / (norm1 * norm2)

    def song_similarity(self, track=None, artist=None):
        '''
        Given information on 1 song, return a similarity score 
        between the song and the user's listening history
            1. Extract the tags of the song from last.fm api;
            2. Calculate the score between the song and user's history
            3. Calculate the score between the song and user's previous selections
        Input:
            - song: track id of the first song

        Output:
            - score: a float number representing similarity between
        '''
        if track is None or artist is None:
            return 0
        track_tags = self.lastapi.get_track_tags(track, artist)
        if track_tags is None:
            return 0
        track_tags = {t['tag_name']: t['tag_count'] for t in track_tags}
        weight = len(self.added_track) * 0.05
        return self.tag_sim_score(track_tags, self.top_tag) * (1 - weight) \
              + self.tag_sim_score(track_tags, self.added_track_tag) * len(self.added_track_tag) * weight
        
    # This will be an interactive function with front end
    def select_ten(self):
        '''
        With the selected tracks, select the top ten with the highest similarity score.
        The top_tracks and recent_tracks will have lower weight compared to added_tracks.

        Input:
            - None, just use self.selected()
        
        Output:
            - ten_songs: A list of {'track_name': 't1', 'artist_name': 'a1'} from database, with length at most 10.
            - scores: A list of similarity scores corresponding to the songs.
        '''
        scores = []
        # Random sampling, prevent too much tracks
        # pdb.set_trace()
        if len(self.selected) > 300:
            self.selected = random.sample(self.selected, 300)
        track_infos = self.dbapi.get_track_info(self.selected)
        for t in track_infos:
            # There are certain tracks not in the database
            if t is None:
                continue
            track, artist = t[1], t[2]
            if (track, artist) in self.visited:
                continue
            scores.append((track, artist, self.song_similarity(track, artist)))
        sorted_scores = sorted(scores, key=lambda x: x[2], reverse=True)
        sorted_scores = [score for score in sorted_scores if score[2] != 0.0]
        # Format output
        ten_songs = [{'track_name': t[0], 'artist_name': t[1]} for t in sorted_scores[:10]]
        scores = [{'score': t[2]} for t in sorted_scores[:10]]
        return ten_songs, scores

    # Dependent with self.change_mode
    def select_songs(self, arg=None):
        '''
        Select ~ tracks according to the current mode.
        arg is either: a tag or an artist name
        '''
        if self.mode == 'tag':
            self.selected = self.select_tag_songs(arg)
        else:
            self.selected = self.select_artist_songs(arg)
    
    def select_tag_songs(self, tag=None):
        '''
        In 'tag' mode, according to how the selected tag goes with other tags in
        users' listening history, select songs with grouped tags from database.

        Input:
            - tag: The target tag selected by the user
        Output:
            - songs: A list of track_id from database
        '''
        tag_comb = list()
        # list(tag_name)
        apperance = dict()
        for taglist in self.top_track_tags:
            if tag in taglist:
                for t, c in taglist.items():
                    if t not in apperance:
                        apperance[t] = c
                    else:
                        apperance[t] += c

        for taglist in self.rec_track_tags:
            if tag in taglist:
                for t, c in taglist.items():
                    if t not in apperance:
                        apperance[t] = c
                    else:
                        apperance[t] += c
        # pdb.set_trace()
        sort_dic = sorted(apperance.items(), key=lambda x: x[1], reverse=True)
        tag_comb.append(tag)
        added = 0
        for t, c in sort_dic:
            if t == tag:
                continue
            tag_comb.append(t)
            added += 1
            if added >= 2:
                break
        # pdb.set_trace()
        # convert tag names into tag id
        tag_ids = self.dbapi.get_tag_id(tag_comb)

        return self.dbapi.get_track_with_tags(tag_comb)
    
    def select_artist_songs(self, artist=None):
        '''
        In 'artist' mode, select 100 tracks from the artist's top_tracks through last.fm API.

        Input:
            - artist: The target artist selected by the user
        
        Output:
            - songs: A list of track_id from database API
        '''
        # Will get 50 tracks
        top_tracks = self.lastapi.get_artist_top_tracks(artist)
        # The track id used in database API
        songs = [artist + ': ' + t['track_name'] for t in top_tracks]
        return songs
    
    def close_server(self):
        '''
        Close connection to the database
        '''
        self.dbapi.close_connection()

def main():
    user = SelfListening()
    user.change_mode('Miles+Davis') # Testing purpose
    ten, score = user.select_ten()
    pdb.set_trace()
    print(user.top_tag)
    print(user.select_tag_songs('Classic Rock'))
    tag1 = {1: 100, 3: 96, 5: 77, 14: 40}
    tag2 = {1: 100, 2: 80, 3: 60, 4: 30}
    score = user.tag_sim_score(tag1, tag2)
    print(score)
    tag3 = {1: 100, 2: 70, 3: 50}
    tag4 = {1: 100, 2: 80, 3: 40}
    tag5 = {1: 100, 3: 95, 2: 67}
    score2 = user.tag_sim_score(tag3, tag4)
    score3 = user.tag_sim_score(tag4, tag5)
    print(score2)
    print(score3)
    # Testing purpose
    # user.lastapi.get_top_artist('rj')

if __name__ == "__main__":
    main()