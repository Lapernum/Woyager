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
        api_key="your openai api key",
    )

    completion = client.chat.completions.create(
    model="gpt-4",
    temperature=0,
    messages=[
        {"role": "user", "content": "Based on the artists, describe a user's music taste with 2-5 genre words and scores. E.g., Punk: 0.7, Indie: 0.8, Alternative: 0.9. " + str(top_artists)},
    ]
    )
    return completion.choices[0].message.content






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




