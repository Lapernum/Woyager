"""API Methods for fetching data from database and Last.fm API"""
import requests
import json
import time
import datetime
import mysql.connector
from mysql.connector import errorcode


from Data.utils import normalizeTag

# Fetches user features from API.
class lastfm_api:
    def __init__(self, path):
        conf = open(path)
        conf_data = json.load(conf)
        self.api_key = conf_data["API_KEY"]
        self.base_url = 'http://ws.audioscrobbler.com/2.0/'
    

    def get_artist_name(self, artist_id):
        """Get the artist name from last.fm API.

        Args:
            artist_id (String): the mbid of the artist
        
        Returns:   
            artist_name(String)
        """
        url = f'{self.base_url}?method=artist.getInfo&mbid={artist_id}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            # print(data)
            artist_name = data['artist']['name']
            return artist_name
        else:
            return None
    
    def get_artist_info(self, artist_name):
        """Get the artist info from last.fm API.

        Args:
            artist_name (String): the name of the artist
            track_name (String): the name of the track

        Returns:
            Dict: a dict of the artist's info in this format
                {"artist_name", "artist_url"}]
        """
        url = f'{self.base_url}?method=artist.getInfo&artist={artist_name}&&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            artist_name = data['artist']['name']
            artist_url = data['artist']['url']
            return {'artist_name': artist_name, 'artist_url': artist_url}
        else:
            return None
        
    def get_track_id(self, track_name, artist_name):
        """Get the track id from last.fm API.

        Args:
            track_name (String): the name of the track
            artist_name (String): the name of the artist of the track

        Returns:
            track_id(String)
        """
        url = f'{self.base_url}?method=track.getInfo&artist={artist_name}&track={track_name}&api_key={self.api_key}&format=json'
        response = requests.get(url)

        if response.status_code == 200:
            try:
                data = response.json()
                track_id = data['track']['mbid']
                return track_id
            except:
                return None
        else:
            return None

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


    def get_recent_tracks(self, username, page_limit=10):
        """Get the user's recent tracks with pagination.

        Args:
            username (str): The username of the user.
            page_limit (int): Maximum number of pages to fetch.

        Returns:
            list: A list of the user's recent tracks in this format
                [{"track_name", "track_url", "listened_at", "artist_id"}, ..., ...]
        """
        recent_tracks = []
        page = 1

        while  page <= page_limit:
            url = (f'{self.base_url}?method=user.getRecentTracks&user={username}'
                f'&api_key={self.api_key}&format=json&limit=100&page={page}')
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                total_pages = int(data['recenttracks']['@attr']['totalPages'])  # Get total number of pages

                for track in data['recenttracks']['track']:
                    # Sometimes the track doesn't have a date (currently playing track), so we check for its existence
                    if 'date' in track:
                        track_name = track['name']
                        track_url = track['url']
                        timestamp = int(track['date']['uts'])
                        listened_at = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        artist_id = track['artist']['mbid']
                        artist_name = track['artist']['#text']
                        recent_tracks.append({
                            'track_name': track_name,
                            'track_url': track_url,
                            'listened_at': listened_at,
                            'artist_id': artist_id,
                            'artist_name': artist_name
                        })
            else:
                # Break out of the loop if there's an HTTP error
                break

            page += 1  # Increment to the next page

        return recent_tracks

    def get_top_tracks(self, username):
        """Get the user's top tracks.

        Args:
            username (String): the username of the user

        Returns:
            List: a list of the user's top tracks in this format
                [{"track_name", "track_url", "track_listening_count", "artist_id"}, ..., ...]
                where listened_at has been transformed from a timestamp into a python string
        """
        url = f'{self.base_url}?method=user.getTopTracks&user={username}&api_key={self.api_key}&limit=100&format=json&page=1'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            top_tracks = []
            for track in data['toptracks']['track']:
                track_name = track['name']
                track_url = track['url']
                count = int(track['playcount'])
                artist_id = track['artist']['mbid']
                artist_name = track['artist']['name']
                top_tracks.append({'track_name': track_name, 'track_url': track_url, 'track_listening_count': count, 'artist_id': artist_id, 'artist_name': artist_name})
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
        url = f'{self.base_url}?method=user.getTopArtists&user={username}&api_key={self.api_key}&format=json&limit=100&format=json&page=1'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            top_artists = []
            for artist in data['topartists']['artist']:
                url = artist['url']
                count = int(artist['playcount'])
                start = len("https://www.last.fm/music/")
                artist_name = url[start:]
                top_artists.append({'artist_name' : artist_name, 'artist_listening_count' : count, 'artist_url': url})
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
        
    def get_user_features(self, username):
        """Get a user's features from last.fm API.

        Args:
            username (String): the username of the user 

        Returns:
            Dict: a dict of the user's features in this format
                {"top_tracks", "top_artists"}
        """
        top_tracks = self.get_top_tracks(username)
        top_artists = self.get_top_artist(username)
        top_tracks_dict = {}
        top_artists_dict = {}

        for track in top_tracks:
            url = track['track_url']
            start = len("https://www.last.fm/music/")
            end = url.index("/_/")

            artist_name = url[start:end]
            track_id = artist_name + ": " + track['track_name']            
            track_listening_count = track['track_listening_count']
            top_tracks_dict[track_id] = track_listening_count
        
        for artist in top_artists:
            artist_name = artist['artist_name']
            artist_listening_count = artist['artist_listening_count']
            top_artists_dict[artist_name] = artist_listening_count


        return {"top_tracks": top_tracks_dict, "top_artists": top_artists_dict}
        
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
                [{"artist_name", "artist_url"}, ..., ...]
        """
        artist_list = [(artist["artist_name"], artist["artist_url"]) for artist in artists]

        sql_save = "INSERT IGNORE INTO Artists (artist_name, artist_url) VALUES (%s, %s)"

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
        sql_save = "INSERT IGNORE INTO Tracks (track_id, track_name, track_url, artist_name) VALUES (%s, %s, %s, %s)"
        track_list = [(track["track_id"], track["track_name"], track["track_url"], track["artist_name"]) for track in tracks]
        try:
                self.cnx_cursor.executemany(sql_save, track_list)
                self.cnx.commit()
                return 

        except Exception as e:
            print(f"Error when saving tracks: {e}")

    
    def save_top_tracks(self, user_id, top_tracks):
        """Save a list of top tracks of a given user to the database.

        Args:
            username (String): the name of the user
            top_tracks (List): a list of tracks in this format
                [{"track_id", "track_listening_count"}, ..., ...]
        """

        track_list = [(user_id, track["track_id"], track["track_listening_count"]) for track in top_tracks]

        sql_save = "INSERT INTO Top_track (user_id, track_id, track_listening_count) VALUES (%s, %s, %s)"

        self.cnx_cursor.executemany(sql_save, track_list)
        self.cnx.commit()
        return
    
    def save_top_artists(self, user_id, top_artists):
        """Save a list of top artists of a given user to the database.

        Args:
            username (String): the name of the user
            top_artists (List): a list of artists in this format
                [{"artist_id", "artist_listening_count"}, ..., ...]
        """

        artist_list = [(user_id, artist["artist_name"], artist["artist_listening_count"]) for artist in top_artists]

        sql_save = "INSERT IGNORE INTO Top_artist (user_id, artist_name, artist_listening_count) VALUES (%s, %s, %s)"

        self.cnx_cursor.executemany(sql_save, artist_list)
        self.cnx.commit()
        return
    
    def save_listening_history(self, user_id, recent_tracks):
        """Save a list of recent tracks of a given user to the database.

        Args:
            userid (Int): the id of the user
            recent_tracks (List): a list of tracks in this format
                [{"track_id", "listened_at"}, ..., ...]
        """
        track_list = [(user_id, track["track_id"], track["listened_at"]) for track in recent_tracks]

        print(track_list)

        sql_save = "INSERT IGNORE INTO Listening_history (user_id, track_id, listened_at) VALUES (%s, %s, %s)"

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
        """ Get a user's recent tracks and listening history from database.

        Args:
            user_id (int)

        Returns:
            recent_tracks: a Dict of tracks in this format
                [{key: track_id, value: list[timestamp]}, ..., ...]
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = """
        SELECT Tracks.track_name, Listening_history.listened_at
        FROM listening_history
        JOIN Tracks ON Listening_history.track_id = Tracks.track_id
        WHERE Listening_history.user_id = %s
        """
        cursor.execute(query, (user_id,))
        recent_tracks = {}
        for row in cursor.fetchall():
            track_name = row['track_name']
            listened_at = row['listened_at']
            if track_name in recent_tracks:
                recent_tracks[track_name].append(listened_at)
            else:
                recent_tracks[track_name] = [listened_at]

        return recent_tracks
    
    def get_top_tracks(self, user_id):
        """ Get a user's top tracks and play counts from database.

        Args:
            user_id (int)

        Returns:
            top_tracks: a Dict of tracks in this format
                [{key: track_id, value: track_listening_count}, ..., ...]
                 
        """
        query = """
        SELECT Top_track.track_id, Top_track.track_listening_count
        FROM Top_track
        WHERE Top_track.user_id = %s
        """
        cursor = self.cnx.cursor(dictionary=True)
        cursor.execute(query, (user_id,))
        top_tracks = {}
        
        for row in cursor.fetchall():
            track_id = row['track_id']
            track_listening_count = row['track_listening_count']
            top_tracks[track_id] = track_listening_count

        cursor.close()
        return top_tracks
    
    def get_top_artist(self, user_id):
        """ Get a user's top artists and play counts from database.

        Args:
            user_id (int)

        Returns:
            top_artist: a Dict of artists in this format
                [{key: artist_id, value: artist_listening_count}, ..., ...]
        """
        query = """
        SELECT Top_artist.artist_name, Top_artist.artist_listening_count
        FROM Top_artist
        WHERE Top_artist.user_id = %s
        """
        cursor = self.cnx.cursor(dictionary=True)
        cursor.execute(query, (user_id,))
        top_artist = {}
        for row in cursor.fetchall():
            artist_name = row['artist_name']
            artist_listening_count = row['artist_listening_count']
            top_artist[artist_name] = artist_listening_count

        return top_artist
    
    def get_all_listening_history_tracks(self):
        """ Fetches all tracks from the listening history table.

        Args:
            None

        Returns:
            historyTracks_dict: a Dict of tracks in this format
                [{key: track_name, value: track_id}, ..., ...]
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = """
        SELECT Tracks.track_name, Listening_history.track_id 
        FROM Listening_history 
        JOIN Tracks ON Listening_history.track_id = Tracks.track_id
        """
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
                [{key: track_name, value: track_id}, ..., ...]
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = """
        SELECT Tracks.track_name, Top_track.track_id 
        FROM Top_track 
        JOIN Tracks ON Top_track.track_id = Tracks.track_id"""
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
                [{key: artist_name, value: artist_id}, ..., ...]
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = """
        SELECT Artists.artist_name, Top_artist.artist_id 
        FROM Top_artist 
        JOIN Artists ON Top_artist.artist_id = Artists.artist_id
        """
        cursor.execute(query)
        top_artist = cursor.fetchall()
        artist_dict = {artist['artist_name']: artist['artist_id'] for artist in top_artist}
        return artist_dict
    
    def get_all_users(self):
        """Fetches all user IDs from the users table.
        Args:
            None

        Returns:
            list: a list of tuples (user_id, user_name)
        """
        query = "SELECT user_id, user_name FROM Users"
        self.cnx_cursor.execute(query)
        users = self.cnx_cursor.fetchall()
        return users
    
    def get_artist_name(self, artist_id):
        """Get the artist name from Artists table.

        Args:
            artist_id (String): the mbid of the artist

        Returns:
            artist_name(String)
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = "SELECT artist_name FROM Artists WHERE artist_id = %s"
        cursor.execute(query, (artist_id),)
        result = cursor.fetchone()
        if result:
            return result['artist_name']
        else:
            return None

    def get_artist_top_tags(self, artist_id):
        """Get the artist's top tags from Artist_Tag table.

        Args:
            artist_id (String): the mbid of the artist

        Returns:
            A list of tag IDs
            ["tag1", "tag2", ..., ...]
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = "SELECT tag_id FROM Artist_Tag WHERE artist_id = %s"""
        cursor.execute(query, (artist_id,))
        tags = cursor.fetchall()
        tag_ids = [tag['tag_id'] for tag in tags]
        return tag_ids

    def get_track_top_tags(self, track_id):
        """Get the track's top tags from Track_tag table.

        Args:
            track_id (String)

        Returns:
            A list of tag IDs
            ["tag1", "tag2", ..., ...]
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = "SELECT tag_id FROM Track_tag WHERE artist_id = %s"
        cursor.execute(query, (track_id,))
        tags = cursor.fetchall()
        tag_ids = [tag['tag_id'] for tag in tags]
        return tag_ids

    def get_tag_dict(self):
        """Fetches all tag names and their IDs from Tags table.
        
        Args:
            None

        Returns:
            A Dict of tag name and tag id
            [{key: tag_name, value: tag_id}, ..., ...]
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = "SELECT tag_id, tag_name FROM Tags"
        cursor.execute(query)
        tags = cursor.fetchall()
        tag_dict = {tag['tag_name']: tag['tag_id'] for tag in tags}
        return tag_dict

    def get_track_with_tags(self, tags_id_list):
        """Retrieves tracks that include all specified tags.

        Args:
            tags_id_list (list): A list of tag IDs (3-4 tags).

        Returns:
            list: A list of track IDs that include all specified tags.
            [{"track_id"}, ..., ...]
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = """
        SELECT track_id 
        FROM Track_tag 
        WHERE tag_id IN %s
        GROUP BY track_id
        HAVING COUNT(DISTINCT tag_id) = %s
        """
        cursor.execute(query, (tuple(tags_id_list), len(tags_id_list)))
        tracks = cursor.fetchall()
        track_ids = {track['track_id'] for track in tracks}
        return track_ids
        
    def get_artist_from_track(self, track_id):
        """Get artist_id with the input track_id
        
        Args:
            track_id(String)

        Returns:
            artist_id(String)
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = "SELECT artist_id FROM Tracks Where Tracks.track_id = %s"
        cursor.execute(query, (track_id,))
        result = cursor.fetchone()
        if result:
            return result['artist_id']
        else:
            return None
    
    def get_user_features(self, user_id):
        """Get a user's features from database.

        Args:
            user_id (int)

        Returns:
            Dict: a dict of the user's features in this format
                {"recent_tracks", "top_tracks", "top_artists"}
        """
        top_tracks = self.get_top_tracks(user_id)
        top_artists = self.get_top_artist(user_id)
        return {"top_tracks": top_tracks, "top_artists": top_artists}
        
    def clear_table(self, table_name):
        """Clear a table.

        Args:
            table_name (str): The name of the table to clear.
        """
        sql_clear = f"TRUNCATE TABLE {table_name}"
        self.cnx_cursor.execute(sql_clear)
        self.cnx.commit()


    def close_connection(self):
        self.cnx.close()
