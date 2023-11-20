import datetime
import math
import pandas as pd
import numpy as np
import urllib
import ast
import numpy as np
import math
from openai import OpenAI


def calculate_recent_tracks_score(recent_tracks):
    """
    calculate the score of user's recent_tracks feature
    :param recent_tracks: Dict {key: track_id, value: list[timestamp]}
    :return: Dict {key: track_id, value: score}
    """
    tracks_score = {}
    current_time = datetime.datetime.now()
    current_day = current_time.day
    current_month = current_time.month
    current_year = current_time.year
    # for each track, use the formula y = e^(-0.01t) to calculate the weights of each track and store them in track_score
    for track in recent_tracks.keys():
        tracks_score[track] = 0
        for i in range(len(recent_tracks[track])):
            track_day = recent_tracks[track][i].day
            track_month = recent_tracks[track][i].month
            track_year = recent_tracks[track][i].year
            difference = (current_year - track_year) * 365 + (current_month - track_month) * 30 + (current_day - track_day)
            tracks_score[track] += math.exp(-0.01 * (difference))

    #normalzie track_score with minimax normalization
    track_score_lst = list(tracks_score.values())
    track_score_lst.sort()
    track_score_min = track_score_lst[0]
    track_score_max = track_score_lst[-1]
    for track in tracks_score.keys():
        tracks_score[track] = (tracks_score[track] - track_score_min) / (track_score_max - track_score_min)*0.95 + 0.05
    return tracks_score

    


def calculate_top_tracks_score(top_tracks):
    """
    calculate the score of user's top_tracks feature
    :param top_tracks: Dict {key: track_id, value: play_count}
    :return: Dict {key: track_id, value: score}
    """
    tracks_score = {}
    for track in top_tracks.keys():
        tracks_score[track] = 0
        tracks_score[track] += top_tracks[track]

    #normalzie track_score with minimax normalization
    track_score_lst = list(tracks_score.values())
    track_score_lst.sort()
    track_score_min = track_score_lst[0]
    track_score_max = track_score_lst[-1]
    for track in tracks_score.keys():
        tracks_score[track] = (tracks_score[track] - track_score_min) / (track_score_max - track_score_min)*0.95 + 0.05
    return tracks_score


def calculate_top_artists_score(top_artists):
    """
    calculate the score of user's top_artists feature
    :param top_artists: List [artist_name]
    :return: Dict {key: artist_id, value: score}
    """
    artists_score = {}
    for artist in top_artists.keys():
        artists_score[artist] = 0
        artists_score[artist] += top_artists[artist]

    #normalzie artist_score with minimax normalization
    artist_score_lst = list(artists_score.values())
    artist_score_lst.sort()
    artist_score_min = artist_score_lst[0]
    artist_score_max = artist_score_lst[-1]
    for artist in artists_score.keys():
        artists_score[artist] = (artists_score[artist] - artist_score_min) / (artist_score_max - artist_score_min)*0.95 + 0.05
    return artists_score


def fetch_user_tag(top_artists):
    """
    Fetches the top three tags of the user based on the top artists preference of a user
    :param top_artists: list of artists
    :return: top three tags with each tag as a string
    """
    if not top_artists:
        return ""
    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key="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",
    )

    completion = client.chat.completions.create(
    model="gpt-4",
    temperature=0,
    messages=[
        {"role": "user", "content": "Based on the artists, describe a user's music taste with 2-5 genre words and scores. E.g., Punk: 0.7, Indie: 0.8, Alternative: 0.9. " + str(top_artists)},
    ]
    )
    return completion.choices[0].message.content


def get_track_id(track_name, conn):
    """
    Input:
        - track_name: The name of the track.
    Output:
        - track_id: The ID of the track.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT track_id FROM Tracks WHERE track_name = ?", (track_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def get_artist_id(artist_name, conn):
    """
    Input:
        - artist_name: The name of the artist.
    Output:
        - artist_id: The ID of the artist.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT artist_id FROM Artists WHERE artist_name = ?", (artist_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None


def transform_user_feature_to_ids(user_feature):
    """
    Input:
        - user_feature: dict{'Recent tracks': Recent tracks with names, 'Top tracks': Top tracks with names, 'Top artists':Top artists with names}
    Output:
        - user_feature: dict{'Recent tracks': Recent tracks with ids, 'Top tracks': Top tracks with ids, 'Top artists':Top artists with ids}
    """
    # Convert track names in Recent tracks to track_ids
    recent_tracks_ids = {get_track_id(key): value for key, value in user_feature['Recent tracks'].items() if
                         get_track_id(key)}

    # Convert track names in Top tracks to track_ids
    top_tracks_ids = {get_track_id(key): value for key, value in user_feature['Top tracks'].items() if
                      get_track_id(key)}

    # Convert artist names in Top artists to artist_ids
    top_artists_ids = {get_artist_id(key): value for key, value in user_feature['Top artists'].items() if
                       get_artist_id(key)}

    return {
        'Recent tracks': recent_tracks_ids,
        'Top tracks': top_tracks_ids,
        'Top artists': top_artists_ids
    }

def calculate_user_distance(user_name):
    """
    calculate the distance between the user and all other users in the database
    :param user_name: the name of the user
    :return: Dict {key: user_id, value: distance}
    """
    user_feature = api_get_user_feature(user_name)
    user_top_artists = user_feature['Top artists']
    user_tags = fetch_user_tag(user_top_artists)
    user_tags = {tag_score.split(":")[0].strip(): float(tag_score.split(":")[1].strip())
                 for tag_score in user_tags.split(",")}

    #transform user_feature from name to ids
    user_feature = transform_user_feature_to_ids(user_feature)

    user_recent_tracks = user_feature['Recent tracks']
    user_top_tracks = user_feature['Top tracks']
    user_top_artists = user_feature['Top artists']


    recent_tracks = pd.read_csv('user_features/recent_tracks.csv')
    top_tracks = pd.read_csv('user_features/top_tracks.csv')
    top_artists = pd.read_csv('user_features/top_artists.csv')
    tags = pd.read_csv('user_features/tags.csv')

    #convert user recent tracks to a model input array
    track_ids = [int(col.split("Recent Track Score ")[1]) for col in recent_tracks.columns if
                 col.startswith("Recent Track Score ")]
    recent_tracks_dict = {track_ids[i]: i for i in range(len(track_ids))}
    user_recent_tracks_array =np.zeros(len(track_ids))
    for track_id in user_recent_tracks.keys():
        user_recent_tracks_array[recent_tracks_dict[track_id]] = user_recent_tracks[track_id]

    #convert user top tracks to a model input array
    track_ids = [int(col.split("Top Track Score ")[1]) for col in top_tracks.columns if
                    col.startswith("Top Track Score ")]
    top_tracks_dict = {track_ids[i]: i for i in range(len(track_ids))}
    user_top_tracks_array = np.zeros(len(track_ids))
    for track_id in user_top_tracks.keys():
        user_top_tracks_array[top_tracks_dict[track_id]] = user_top_tracks[track_id]

    #convert user top artists to a model input array
    artist_ids = [int(col.split("Top Artist Score ")[1]) for col in top_artists.columns if
                    col.startswith("Top Artist Score ")]
    top_artists_dict = {artist_ids[i]: i for i in range(len(artist_ids))}
    user_top_artists_array = np.zeros(len(artist_ids))
    for artist_id in user_top_artists.keys():
        user_top_artists_array[top_artists_dict[artist_id]] = user_top_artists[artist_id]

    #convert user tags to a model input array
    tags_lst = [col.split("Tag Score ")[1] for col in tags.columns if
                    col.startswith("Tag Score ")]
    tags_dict = {tags_lst[i]: i for i in range(len(tags_lst))}
    user_tags_array = np.zeros(len(tags_lst))
    for tag in user_tags:
        user_tags_array[tags_dict[tag]] = user_tags[tag]


    # convert database user features to model input arrays
    recent_tracks_array = recent_tracks.drop(columns=['user_id']).values
    top_tracks_array = top_tracks.drop(columns=['user_id']).values
    top_artists_array = top_artists.drop(columns=['user_id']).values
    tags_array = tags.drop(columns=['user_id']).values

    #calculate the distance between the user and all other users in the database
    recent_distances = np.sqrt(((recent_tracks_array - user_recent_tracks_array) ** 2).sum(axis=1))
    top_tracks_distances = np.sqrt(((top_tracks_array - user_top_tracks_array) ** 2).sum(axis=1))
    top_artists_distances = np.sqrt(((top_artists_array - user_top_artists_array) ** 2).sum(axis=1))
    tags_distances = np.sqrt(((tags_array - user_tags_array) ** 2).sum(axis=1))

    #calculate the score of each track based on the distance
    total_distance = 0.25 * recent_distances + 0.25 * top_tracks_distances + 0.25 * top_artists_distances + 0.25 * tags_distances

    #normalize the distance score
    total_distance = (total_distance - np.min(total_distance)) / (np.max(total_distance) - np.min(total_distance))

    # Get the indices of the top 100 closest users
    top_10_indices = np.argsort(total_distance)[:100]

    # Get the user IDs of the top 100 closest users
    top_10_user_ids = recent_tracks['user_id'].values[top_10_indices]

    # Get the distances of the top 100 closest users
    top_10_distances = total_distance[top_10_indices]

    # Pair the top 100 user IDs with their respective distances
    user_distance_pairs = dict(zip(top_10_user_ids, top_10_distances))

    return user_distance_pairs





def urls_to_text(url_encoded_list):
    """
    Converts a list of URL-encoded strings to a list of regular text strings.
    
    Args:
    url_encoded_list (list): A list of URL-encoded strings.
    
    Returns:
    list: A list of decoded regular text strings.
    """
    # Decode each URL-encoded string in the list
    return [urllib.parse.unquote_plus(url) for url in url_encoded_list]




