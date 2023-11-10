"""API Methods for fetching data from database and Last.fm API"""
import requests
import json
import mysql.connector
from mysql.connector import errorcode

class createUserDataset:
    def __init__(self): 
        conf = open("conf.json")
        conf_data = json.load(conf)
        self.api_key = conf_data["API_KEY"]
        self.sql_username = conf_data["SQL_USERNAME"]
        self.sql_password = conf_data["SQL_PASSWORD"]
        self.sql_host = conf_data["SQL_HOST"]
        self.sql_database = conf_data["SQL_DATABASE"]
        self.ssl_ca = conf_data["SQL_SSL_CA"]


    # Return a list of info json of friends
    def get_user_friends(self, username):
        response = requests.get(
            "https://ws.audioscrobbler.com/2.0/?method=user.getfriends&user= " + username + "&api_key= " + self.api_key + "&format=json")
        data = response.json()
        friends = data["friends"]["user"]
        return friends

    def save_users(self, users):
        config = {
            'host': self.sql_host,
            'user': self.sql_username,
            'password': self.sql_password,
            'database': self.sql_database,
            'client_flags': [mysql.connector.ClientFlag.SSL],
            'ssl_ca': self.ssl_ca
        }

        try:
            cnx = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with the user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            return

        cnx_cursor = cnx.cursor()

        sql_fetch = "SELECT user_name FROM Users"
        cnx_cursor.execute(sql_fetch)
        already_in = cnx_cursor.fetchall()
        already_ins = [a[0] for a in already_in]

        user_list = []
        for user in users:
            if user["name"] not in already_ins:
                user_list.append((user["name"], user["url"]))

        sql_save = "INSERT IGNORE INTO Users (user_name, user_url) VALUES (%s, %s)"

        cnx_cursor.executemany(sql_save, user_list)
        cnx.commit()
        cnx.close()

        return
      
def fetch_high_quality_users(conn):
    """
    Fetches high-quality users from the database
    high-quality users are defined as users who have listened to at least 300 recent tracks (can be repetitive)
    :param conn: database connection
    :return: list of user ids
    """
    raise NotImplementedError

def get_user_feature(conn, user_id):
    """
    Input:
        - user_id: The ID of the user.
    Output:
        - From Database: dict{'Recent tracks': Recent tracks, 'Top tracks': Top tracks, 'Top artists':Top artists}
            1. Recent tracks: Dict {key: track_id, value: list[timestamp]}
            2. Top tracks: Dict {key: track_id, value: count}
            3. Top artists: Dict {key: artist_id, value: count}
    """
    raise NotImplementedError

def api_get_user_feature(user_name):
    """
    Input:
        - user_name: The name of the user.
    Output:
        - From API: dict{'Recent tracks': Recent tracks, 'Top tracks': Top tracks, 'Top artists':Top artists}
            1. Recent tracks: Dict {key: track_name, value: list[timestamp]}
            2. Top tracks: Dict {key: track_name, value: count}
            3. Top artists: Dict {key: artist_name, value: count}
    """
    raise NotImplementedError

# Fetches user features from API.
class api_get_user_feature:
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
class database_get_user_feature:
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
        querry = """
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
        querry = """
        SELECT Artist.artist_name, top_artist.Count
        FROM Artist
        JOIN top_artist ON Artist.artist_id = top_artist.artist_id
        WHERE top_artist.user_id = %s
        """
        cursor.execute(query, (user_id,))
        top_tracks = {}
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
        historyTracks_dict = {track['track_name']: track['track_id'] for track in top_tracks}
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