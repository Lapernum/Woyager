"""API Methods for fetching data from database and Last.fm API"""

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


