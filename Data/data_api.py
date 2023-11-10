"""API Methods for fetching data from database and Last.fm API"""
import requests
import json
import mysql.connector
from mysql.connector import errorcode

# Fetches user features from API.
class lastfm_api:
    def __self__(self):
        conf = open("conf.json")
        conf_data = json.load(conf)
        self.api_key = conf_data["API_KEY"]
        self.base_url = 'http://ws.audioscrobbler.com/2.0/'

    # Return a list of info json of friends
    def get_user_friends(self, username):
        url = f'https://ws.audioscrobbler.com/2.0/?method=user.getfriends&user={username}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            friends = data["friends"]["user"]
            return friends
        else:
            return None

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
                track_id = track['id']
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

    def get_track_id(self, track_name, artist_name):
        url = f'{self.base_url}?method=track.getInfo&artist={artist_name}&track={track_name}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            track_id = data["track"]["mbid"]
            return track_id
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
    def __init__(self):
        conf = open("conf.json")
        conf_data = json.load(conf)
        self.sql_username = conf_data["SQL_USERNAME"]
        self.sql_password = conf_data["SQL_PASSWORD"]
        self.sql_host = conf_data["SQL_HOST"]
        self.sql_database = conf_data["SQL_DATABASE"]
        self.ssl_ca = conf_data["SQL_SSL_CA"]

        self.conn = mysql.connector.connect(
            host=self.sql_host,
            user=self.sql_username,
            password=self.sql_password,
            database=self.sql_database,
            ssl_ca=self.ssl_ca
        )

        try:
            self.cnx = mysql.connector.connect(**self.conn)
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
        self.cnx.close()

        return newly_added_length
    
    def save_top_tracks(self, username, top_tracks):
        sql_getuserid = "SELECT user_id FROM Users WHERE user_name = %s"
        self.cnx_cursor.execute(sql_getuserid, username)
        user_id = self.cnx_cursor.fetchall()[0]

        sql_fetch = "SELECT track_id FROM Top_track WHERE user_id = %s"
        self.cnx_cursor.execute(sql_fetch, user_id)
        already_in = self.cnx_cursor.fetchall()
        already_ins = [a[0] for a in already_in]

        track_list = []
        for track in top_tracks:
            if track["name"] not in already_ins:
                user_list.append((user["name"], user["url"]))
        
        newly_added_length = len(user_list)

        sql_save = "INSERT IGNORE INTO Users (user_name, user_url) VALUES (%s, %s)"

        self.cnx_cursor.executemany(sql_save, user_list)
        self.cnx.commit()
        self.cnx.close()

        return newly_added_length

    def get_recent_tracks(self, user_id):
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
    
    def GetAllListeningHistoryTracks(self):
        cursor = self.conn.cursor(dictionary=True)
        query = "SELECT tracks.track_name, listening_history.track_id FROM listening_history JOIN tracks ON listening_history.track_id = tracks.track_id"
        cursor.execute(query)
        history_tracks = cursor.fetchall()
        historyTracks_dict = {track['track_name']: track['track_id'] for track in history_tracks}
        return historyTracks_dict
    
    def GetAllTopTracks(self):
        cursor = self.conn.cursor(dictionary=True)
        query = "SELECT tracks.track_name, top_track.track_id FROM top_track JOIN tracks ON top_track.track_id = tracks.track_id"
        cursor.execute(query)
        top_tracks = cursor.fetchall()
        topTracks_dict = {track['track_name']: track['track_id'] for track in top_tracks}
        return topTracks_dict
    
    def GetAllTopArtists(self):
        cursor = self.conn.cursor(dictionary=True)
        query = "SELECT Artists.artist_name, top_artist.artist_id FROM top_artist JOIN artists ON top_artist.artist_id = Artists.artist_id"
        cursor.execute(query)
        top_artist = cursor.fetchall()
        artist_dict = {track['artist_name']: track['artist_id'] for artist in top_artist}
        return artist_dict

    def close_connection(self):
        self.conn.close()