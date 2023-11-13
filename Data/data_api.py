"""API Methods for fetching data from database and Last.fm API"""
import requests
import json
import time
import datetime
import mysql.connector
from mysql.connector import errorcode

from .utils import normalizeTag

# Fetches user features from API.
class lastfm_api:
    def __init__(self, path):
        conf = open(path)
        conf_data = json.load(conf)
        self.api_key = conf_data["API_KEY"]
        self.base_url = 'http://ws.audioscrobbler.com/2.0/'

    # Return a list of info json of friends
    def get_user_friends(self, username):
        """Get a user's friends.

        Args:
            username (String): the username of the user

        Returns:
            List: a list of user's friends in this format 
                [{"name", "url", "country", "playlists", "playcount", "image", "realname", "subscriber", "bootstrap", "type"}, ..., ...]
        """
        url = f'https://ws.audioscrobbler.com/2.0/?method=user.getfriends&user={username}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            friends = data["friends"]["user"]
            return friends
        else:
            return None

    def get_recent_tracks(self, username):
        """Get the user's recent tracks.

        Args:
            username (String): the username of the user

        Returns:
            List: a list of the user's recent tracks in this format
                [{"track_name", "track_url", "listened_at", "artist_id"}, ..., ...]
        """
        url = f'{self.base_url}?method=user.getRecentTracks&user={username}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            recent_tracks = []
            for track in data['recenttracks']['track']:
                track_name = track['name']
                track_url = track['url']
                timestamp = track['date']['uts']
                timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%d %b %Y, %H:%M')
                artist_id = track['artist']['mbid']
                recent_tracks.append({'track_name' : track_name, 'track_url': track_url, 'listened_at' : timestamp, 'artist_id': artist_id})
            return recent_tracks
        else:
            return None

    def get_top_tracks(self, username):
        """Get the user's top tracks.

        Args:
            username (String): the username of the user

        Returns:
            List: a list of the user's top tracks in this format
                [{"track_name", "track_url", "listened_at", "artist_id"}, ..., ...]
                where listened_at has been transformed from a timestamp into a python string
        """
        url = f'{self.base_url}?method=user.getTopTracks&user={username}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            top_tracks = []
            for track in data['toptracks']['track']:
                track_name = track['name']
                track_url = track['url']
                count = int(track['playcount'])
                artist_id = track['artist']['mbid']
                top_tracks.append({'track_name': track_name, 'track_url': track_url, 'track_listening_count': count, 'artist_id': artist_id})
            return top_tracks
        else:
            return None

    def get_top_artist(self, username):
        """Get the user's top artists.

        Args:
            username (String): the username of the user

        Returns:
            List: a list of the user's top artists in this format
                [{"artist_id", "artist_name", "artist_listening_count"}, ..., ...]
        """
        url = f'{self.base_url}?method=user.getTopTracks&user={username}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            top_artists = []
            for artist in data['topartists']['artist']:
                artist_id = artist['mbid']
                artist_name = artist['name']
                count = int(artist['playcount'])
                top_artists.append({'artist_id': artist_id, 'artist_name' : artist_name, 'artist_listening_count' : count})
            return top_artists
        else:
            return None
    
    def get_artist_top_tracks(self, artist_name):
        """Get the artist's top tracks.

        Args:
            artist_name (String): the name of the artist

        Returns:
            List: a list of the artist's top tracks in this format
                [{"track_name", "track_listening_count"}, ..., ...]
        """
        url = f'{self.base_url}?method=artist.getTopTracks&artist={artist_name}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            top_tracks = []
            for track in data['toptracks']['track']:
                track_name = track['name']
                count = int(track['playcount'])
                top_tracks.append({'track_name': track_name, 'track_listening_count': count})
            return top_tracks
        else:
            return None
        
    def get_track_tags(self, track_name, artist_name):
        """Get the top tags of the given track.

        Args:
            track_name (String): the name of the track
            artist_name (String): the name of the artist of the track

        Returns:
            List: a list of the track's top tags in this format
                [{"tag_name", "tag_count"}, ..., ...]
        """
        url = f'{self.base_url}?method=track.gettoptags&artist={artist_name}&track={track_name}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            track_tags = []
            for tag in data['toptags']['tag']:
                tag_name = tag['name'].lower()
                tag_count = int(tag['count'])
                track_tags.append((tag_name, tag_count))
            normalized_track_tags = normalizeTag(track_tags, artist_name, track_name, n = 5)
            result_tags = []
            for normalized_tag in normalized_track_tags:
                result_tags.append({'tag_name': normalized_tag[0], 'tag_count': normalized_tag[1]})
            return result_tags
        else:
            return None

    def get_artist_tags(self, artist_name):
        """Get the top tags of the given artist.

        Args:
            artist_name (String): the name of the artist

        Returns:
            List: a list of the artist's top tags in this format
                [{"tag_name", "tag_count"}, ..., ...]
        """
        url = f'{self.base_url}?method=artist.gettoptags&artist={artist_name}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            artist_tags = []
            for tag in data['toptags']['tag']:
                tag_name = tag['name'].lower()
                tag_count = int(tag['count'])
                artist_tags.append((tag_name, tag_count))
            normalized_artist_tags = normalizeTag(artist_tags, artist_name, n = 5)
            result_tags = []
            for normalized_tag in normalized_artist_tags:
                result_tags.append({'tag_name': normalized_tag[0], 'tag_count': normalized_tag[1]})
            return result_tags
        else:
            return None
        
# Fetches user features from the database.
class database_api:
    """
        Input:
            - user_id: The ID of the user.
        Output:
            - Recent tracks: Dict {key: track_id, value: list[timestamp]}
            - Top tracks: Dict {key: track_id, value: count}
            - Top artists: Dict {key: artist_id, value: count}
        
        Input:
            - none
        Output:
            - GetAllListeningHistoryTracks, Dict: {key: track_name, value: track_id}
            - GetAllTopTracks, Dict: {key: track_name, value: track_id}
            - GetAllTopArtists, Dict: {key: artist_name, value: artist_id}
    """
    def __init__(self, path):
        conf = open(path)
        conf_data = json.load(conf)
        self.sql_username = conf_data["SQL_USERNAME"]
        self.sql_password = conf_data["SQL_PASSWORD"]
        self.sql_host = conf_data["SQL_HOST"]
        self.sql_database = conf_data["SQL_DATABASE"]
        self.ssl_ca = conf_data["SQL_SSL_CA"]

        try:
            self.cnx = mysql.connector.connect(
                host=self.sql_host,
                user=self.sql_username,
                password=self.sql_password,
                database=self.sql_database,
                ssl_ca=self.ssl_ca
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with the user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            return

        self.cnx_cursor = self.cnx.cursor()

    def save_users(self, users):
        """Save a list of users into database without duplication.

        Args:
            users (List): a list of users in this format
                [{"name", "url"}, ..., ...]

        Returns:
            int: the number of new users added to the database without duplication
        """
        sql_fetch = "SELECT user_name FROM Users"
        self.cnx_cursor.execute(sql_fetch)
        already_in = self.cnx_cursor.fetchall()
        already_ins = [a[0] for a in already_in]

        user_list = []
        for user in users:
            if user["name"] not in already_ins:
                user_list.append((user["name"], user["url"]))
        
        newly_added_length = len(user_list)

        sql_save = "INSERT IGNORE INTO Users (user_name, user_url) VALUES (%s, %s)"

        self.cnx_cursor.executemany(sql_save, user_list)
        self.cnx.commit()
        return newly_added_length

    def save_artists(self, artists):
        """Save a list of artists into the database.

        Args:
            artists (List): a list of artists in this format
                [{"artist_id", "artist_name", "artist_url"}, ..., ...]
        """
        artist_list = [(artist["artist_id"], artist["artist_name"], artist["artist_url"]) for artist in artists]

        sql_save = "INSERT IGNORE INTO Artists (artist_id, artist_name, artist_url) VALUES (%s, %s, %d)"

        self.cnx_cursor.executemany(sql_save, artist_list)
        self.cnx.commit()
        return
    
    def save_tracks(self, tracks):
        """Save a list of tracks into the database without duplication.

        Args:
            tracks (List): a list of artists in this format
                [{"track_name", "track_url", "artist_id"}, ..., ...]
        
        Returns:
            int: the number of new tracks added to the database without duplication
        """
        sql_fetch = "SELECT track_name, artist_id FROM Tracks"
        self.cnx_cursor.execute(sql_fetch)
        already_in = self.cnx_cursor.fetchall()
        already_ins = [a[0] for a in already_in]

        track_list = []
        for track in tracks:
            if (track["track_name"], track["artist_id"]) not in already_ins:
                track_list.append((track["track_name"], track["track_url"], track["artist_id"]))

        newly_added_length = len(track_list)

        sql_save = "INSERT IGNORE INTO Tracks (track_name, track_url, artist_id) VALUES (%s, %s, %s)"

        self.cnx_cursor.executemany(sql_save, track_list)
        self.cnx.commit()
        return newly_added_length
    
    def save_top_tracks(self, username, top_tracks):
        """Save a list of top tracks of a given user to the database.

        Args:
            username (String): the name of the user
            top_tracks (List): a list of tracks in this format
                [{"track_id", "track_listening_count"}, ..., ...]
        """
        sql_getuserid = "SELECT user_id FROM Users WHERE user_name = %s"
        self.cnx_cursor.execute(sql_getuserid, username)
        user_id = self.cnx_cursor.fetchall()[0]

        track_list = [(user_id, track["track_id"], track["track_listening_count"]) for track in top_tracks]

        sql_save = "INSERT IGNORE INTO Top_track (user_id, track_id, track_listening_count) VALUES (%d, %s, %d)"

        self.cnx_cursor.executemany(sql_save, track_list)
        self.cnx.commit()
        return
    
    def save_top_artists(self, username, top_artists):
        """Save a list of top artists of a given user to the database.

        Args:
            username (String): the name of the user
            top_artists (List): a list of artists in this format
                [{"artist_id", "artist_listening_count"}, ..., ...]
        """
        sql_getuserid = "SELECT user_id FROM Users WHERE user_name = %s"
        self.cnx_cursor.execute(sql_getuserid, username)
        user_id = self.cnx_cursor.fetchall()[0]

        artist_list = [(user_id, artist["artist_id"], artist["artist_listening_count"]) for artist in top_artists]

        sql_save = "INSERT IGNORE INTO Top_artist (user_id, artist_id, artist_listening_count) VALUES (%d, %s, %d)"

        self.cnx_cursor.executemany(sql_save, artist_list)
        self.cnx.commit()
        return
    
    def save_listening_history(self, username, recent_tracks):
        """Save a list of recent tracks of a given user to the database.

        Args:
            username (String): the name of the user
            recent_tracks (List): a list of tracks in this format
                [{"track_id", "listened_at"}, ..., ...]
        """
        sql_getuserid = "SELECT user_id FROM Users WHERE user_name = %s"
        self.cnx_cursor.execute(sql_getuserid, username)
        user_id = self.cnx_cursor.fetchall()[0]

        track_list = [(user_id, track["track_id"], track["listened_at"]) for track in recent_tracks]

        sql_save = "INSERT IGNORE INTO Listening_history (user_id, track_id, listened_at) VALUES (%d, %s, %s)"

        self.cnx_cursor.executemany(sql_save, track_list)
        self.cnx.commit()
        return
    
    def save_tags(self, tags):
        """Save a list of tags into database.

        Args:
            tags (List): a list of tags in this format
                [{"tag_name", "tag_url"}, ..., ...]

        Returns:
            int: the number of new tags added to the database without duplication
        """
        sql_fetch = "SELECT tag_name FROM Tags"
        self.cnx_cursor.execute(sql_fetch)
        already_in = self.cnx_cursor.fetchall()
        already_ins = [a[0] for a in already_in]

        tag_list = []
        for tag in tags:
            if tag["tag_name"] not in already_ins:
                tag_list.append((tag["tag_name"], tag["tag_url"]))
        
        newly_added_length = len(tag_list)

        sql_save = "INSERT IGNORE INTO Tags (tag_name, tag_url) VALUES (%s, %s)"

        self.cnx_cursor.executemany(sql_save, tag_list)
        self.cnx.commit()
        return newly_added_length
    
    def save_track_tag(self, track_id, tags):
        """Save a list of tags of a track to the database.

        Args:
            track_id (String): the mbid of the track
            tags (List): a list of tags in this format
                [{"tag_id", "tag_count"}, ..., ...]
        """
        tag_list = [(tag["tag_id"], track_id, tag["tag_count"]) for tag in tags]

        sql_save = "INSERT IGNORE INTO Track_tag (tag_id, track_id, tag_count) VALUES (%d, %s, %d)"

        self.cnx_cursor.executemany(sql_save, tag_list)
        self.cnx.commit()
        return
    
    def save_artist_tag(self, artist_id, tags):
        """Save a list of tags of an artist to the database.

        Args:
            artist_id (String): the mbid of the artist
            tags (List): a list of tags in this format
                [{"tag_id", "tag_count"}, ..., ...]
        """
        tag_list = [(tag["tag_id"], artist_id, tag["tag_count"]) for tag in tags]

        sql_save = "INSERT IGNORE INTO Artist_tag (tag_id, artist_id, tag_count) VALUES (%d, %s, %d)"

        self.cnx_cursor.executemany(sql_save, tag_list)
        self.cnx.commit()
        return

    def get_recent_tracks(self, user_id):
        """ Get a user's recent tracks and listening history from database

        Args:
            user_id (int)

        Returns:
            recent_tracks: a Dict of tracks in this format
                {key: track_id, value: list[timestamp]}
        """
        cursor = self.conn.cursor(dictionary=True)
        query = """
        SELECT tracks.Track_name, listening_history.listened_at
        FROM listening_history
        JOIN tracks ON listening_history.track_id = tracks.track_id
        WHERE listening_history.user_id = %s
        """
        cursor.execute(query, (user_id,))
        recent_tracks = {}
        for row in cursor.fetchall():
            track_name = row['Track_name']
            listened_at = row['listened_at']
            if track_name in recent_tracks:
                recent_tracks[track_name].append(listened_at)
            else:
                recent_tracks[track_name] = [listened_at]

        return recent_tracks
    
    def get_top_tracks(self, user_id):
        """ Get a user's top tracks and play counts from database

        Args:
            user_id (int)

        Returns:
            top_tracks: a Dict of tracks in this format
                 {key: track_id, value: count}
        """
        cursor = self.conn.cursor(dictionary=True)
        query = """
        SELECT Tracks.tract_name, top_track.Count
        FROM top_track
        JOIN tracks ON top_track.track_id = Tracks.track_id
        WHERE top_track.user_id = %s
        """
        cursor.execute(query, (user_id,))
        top_tracks = {}
        for row in cursor.fetchall():
            track_name = row['Track_name']
            count = row['Count']
            top_tracks[track_name] = count

        return top_tracks
    
    def get_top_artist(self, user_id):
        """ Get a user's top artists and play counts from database

        Args:
            user_id (int)

        Returns:
            top_artist: a Dict of artists in this format
                 {key: artist_id, value: count}
        """
        cursor = self.conn.cursor(dictionary=True)
        query = """
        SELECT Artist.artist_name, top_artist.Count
        FROM Artist
        JOIN top_artist ON Artist.artist_id = top_artist.artist_id
        WHERE top_artist.user_id = %s
        """
        cursor.execute(query, (user_id,))
        top_artist = {}
        for row in cursor.fetchall():
            artist_name = row['artist_name']
            count = row['Count']
            top_artist[artist_name] = count

        return top_artist
    
    def get_all_listening_history_tracks(self):
        """ Fetches all tracks from the listening history.

        Args:
            None

        Returns:
            historyTracks_dict: a Dict of tracks in this format
                {key: track_name, value: track_id}
        """
        cursor = self.conn.cursor(dictionary=True)
        query = "SELECT tracks.track_name, listening_history.track_id FROM listening_history JOIN tracks ON listening_history.track_id = tracks.track_id"
        cursor.execute(query)
        history_tracks = cursor.fetchall()
        historyTracks_dict = {track['track_name']: track['track_id'] for track in history_tracks}
        return historyTracks_dict
    
    def get_all_top_tracks(self):
        """ Fetches all tracks from the top track table.
        Args:
            None

        Returns:
            topTracks_dict: a Dict of tracks in this format
                {key: track_name, value: track_id}
        """
        cursor = self.conn.cursor(dictionary=True)
        query = "SELECT tracks.track_name, top_track.track_id FROM top_track JOIN tracks ON top_track.track_id = tracks.track_id"
        cursor.execute(query)
        top_tracks = cursor.fetchall()
        topTracks_dict = {track['track_name']: track['track_id'] for track in top_tracks}
        return topTracks_dict
    
    def get_all_top_artists(self):
        """Fetches all artists from the top artist table.
        Args:
            None

        Returns:
            artist_dict: a Dict of artists in this format
                {key: artist_name, value: artist_id}
        """
        cursor = self.conn.cursor(dictionary=True)
        query = "SELECT Artists.artist_name, top_artist.artist_id FROM top_artist JOIN artists ON top_artist.artist_id = Artists.artist_id"
        cursor.execute(query)
        top_artist = cursor.fetchall()
        artist_dict = {track['artist_name']: track['artist_id'] for artist in top_artist}
        return artist_dict
    
    def get_all_users(self):
        """Fetches all user IDs from the users table.
        Args:
            None

        Returns:
            all_user_id: A list of user IDs.
        """
        cursor = self.conn.cursor(dictionary=True)
        query = "SELECT user_id FROM Users"
        cursor.execute(query)
        users = cursor.fetchall()
        all_user_id = [user['user_id'] for user in users]
        return all_user_id

    def close_connection(self):
        """Needs modification

        Args:
            tags (List): a list of tags in this format
                [{"tag_name", "tag_url"}, ..., ...]

        Returns:
            int: the number of new tags added to the database without duplication
        """
        self.cnx.close()