import numpy as np
import sys
sys.path.insert(0, "Data")
import data_api

class SelfListening:
    def __init__(self, mode='tag'):
        # The top tracks of the user, list(track_id)
        self.top_track = list()
        # The recent tracks listened by the user, list(track_id)
        self.recent = list()
        # The top artists of the user, list(artist_id)
        self.top_artist = list()
        # The added tracks that is selected by user in the process, list(track_id)
        self.added_track = list()
        # Mode for the recommend step, either 'tag' or 'artist'
        self.mode = mode
        # The selected tracks from select_songs()
        self.selected = list()
        
    def add_track(self, added_song):
        '''
        This function appends the added song selected in "Self-listening Mode" to added_track

        Input:
            - added_song: the track_id of the added song
        
        Output:
            - None
        '''
        self.added_track.append(added_song)

    def change_mode(self, mode='artist'):
        '''
        Changes mode according to mode variable

        Input:
            - mode: either 'tag' or 'artist',
            anythin else will be considered as 'tag'
        '''
        if mode == 'artist':
            self.mode = 'artist'
        else:
            self.mode = 'tag'

    def tag_sim_score(self, tag_dict1=None, tag_dict2=None):
        '''
        This function calculates the similarity score between two dictionary of tags.
        
        Input:
            - tag_dict1: a (tag, count) pair dictionary
            - tag_dict2: a (tag, count) pair dictionary

        Output:
            - score: a float number representing similarity
        '''
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

    def song_similarity(self, song1=None, song2=None):
        '''
        Given information on 2 songs, return a similarity score between the two songs
            1. Extract the tags of the two songs from database;
            2. Extract the top tags of the two artists from database;
            3. Calculate both similarities and sum up to score.
        Input:
            - song1: track id of the first song
            - song2: track id of the second song

        Output:
            - score: a float number representing similarity between two songs
        '''
        raise NotImplementedError
    
    def select_ten(self):
        '''
        With the selected tracks, select the top ten with the highest similarity score.
        The top_tracks and recent_tracks will have lower weight compared to added_tracks.

        Input:
            - None, just use self.selected()
        
        Output:
            - ten_songs: A list of track_id from database, with length at most 10.
            - score: A list of similarity scores corresponding to the songs.
        '''
        raise NotImplementedError

    def select_songs(self, arg=None):
        '''
        Select 100 tracks according to the current mode.
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
        raise NotImplementedError
    
    def select_artist_songs(self, artist=None):
        '''
        In 'artist' mode, select 100 tracks from the artist's top_tracks through last.fm API.

        Input:
            - artist: The target artist selected by the user
        
        Output:
            - songs: A list of track_id from last.fm API
        '''
        raise NotImplementedError

def main():
    user = SelfListening()
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

if __name__ == "__main__":
    main()