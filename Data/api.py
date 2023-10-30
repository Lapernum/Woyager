import requests
import json
import mysql.connector
from mysql.connector import errorcode


# Fetches user features from API.
class LastFMAPI:
    def __self__(self):
        conf = open("conf.json")
        conf_data = json.load(conf)
        self.api_key = conf_data["API_KEY"]
        self.base_url = 'http://ws.audioscrobbler.com/2.0/'

    def get_recent_tracks(self, username):
        url = f'{self.base_url}?method=user.getRecentTracks&user={username}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            recent_tracks = {}
            for track in data['recenttracks']['track']:
                track_name = track['name']
                timestamp = track['date']['uts']
                recent_tracks[track_name] = timestamp
            return recent_tracks
        else:
            return None

    def get_top_tracks(self, username):
        url = f'{self.base_url}?method=user.getTopTracks&user={username}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            top_tracks = {}
            for track in data['toptracks']['track']:
                track_name = track['name']
                count = int(track['playcount'])
                top_tracks[track_name] = count
            return top_tracks
        else:
            return None

    def get_top_artist(self, username):
        url = f'{self.base_url}?method=user.getTopTracks&user={username}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            top_artists = {}
            for artist in data['topartists']['artist']:
                artist_name = artist['name']
                count = int(artist['playcount'])
                top_artists[artist_name] = count
            return top_artists
        else:
            return None
    
    def get_artist_top_tracks(self, artist_name):
        url = f'{self.base_url}?method=artist.getTopTracks&artist={artist_name}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            top_tracks = {}
            for track in data['toptracks']['track']:
                track_name = track['name']
                count = int(track['playcount'])
                top_tracks[track_name] = count
            return top_tracks
        else:
            return None


# Fetches user features from the database.
class Database:
    """
        Input:
            - user_id: The ID of the user.
        Output:
            - From Database: dict{'Recent tracks': Recent tracks, 'Top tracks': Top tracks, 'Top artists':Top artists}
                1. Recent tracks: Dict {key: track_id, value: list[timestamp]}
                2. Top tracks: Dict {key: track_id, value: count}
                3. Top artists: Dict {key: artist_id, value: count}
        
        Input:
            - none
        Output:
            - GetAllListeningHistoryTracks, Dict: {key: track_name, value: track_id}
                    Description: Fetches all tracks from the listening history.
            - GetAllTopTracks, Dict: {key: track_name, value: track_id}
            - GetAllTopArtists, Dict: {key: artist_name, value: artist_id}
    """
    def __init__(self, host, user, password, database):
        conf = open("conf.json")
        conf_data = json.load(conf)
        self.sql_username = conf_data["SQL_USERNAME"]
        self.sql_password = conf_data["SQL_PASSWORD"]
        self.sql_host = conf_data["SQL_HOST"]
        self.sql_database = conf_data["SQL_DATABASE"]
        self.ssl_ca = conf_data["SQL_SSL_CA"]

    def get_recent_tracks(self, user_id):
        raise NotImplementedError
    def get_top_tracks(self, user_id):
        raise NotImplementedError
    def get_top_artist(self, user_id):
        raise NotImplementedError
    def GetAllListeningHistoryTracks(self):
        raise NotImplementedError
    def GetAllTopTracks(self):
        raise NotImplementedError
    def GetAllTopArtists(self):
        raise NotImplementedError