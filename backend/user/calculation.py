import sys
sys.path.append('.')
sys.path.append('./Data')


import os
import pandas as pd
import numpy as np
from data_api import *
from backend.user.user_algorithm import *



def concatenate_feature_csvs(feature):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the 'user_features' directory
    directory = os.path.join(script_dir, 'user_features')    
    
    csv_files = [f"{directory}/{file}" for file in os.listdir(directory) if file.startswith(feature)]

    # Concatenate all the CSV files into a single DataFrame
    df = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)

    return df




def calculate_top_tracks_distance(username, top_tracks_df):
    # get user features
    last_fm = lastfm_api('/Users/ziandong/TreeMusicRecommendation/Data/conf.json')
    user_feature = last_fm.get_user_features(username)
    user_feature['top_tracks'] = calculate_top_tracks_score(user_feature['top_tracks'])

    # convert user features to vector
    # top track vector
    top_track_ids = top_tracks_df.columns[top_tracks_df.columns != "user_id"]
    top_tracks_map = {track_id: idx for idx, track_id in enumerate(top_track_ids)}
    user_top_tracks = np.zeros(len(top_track_ids))
    for track_id  in user_feature['top_tracks']:
        if track_id in top_tracks_map:
            user_top_tracks[top_tracks_map[track_id]] = user_feature['top_tracks'][track_id]


    # convert database user features to model input arrays
    top_tracks = top_tracks_df.drop(columns=['user_id']).values

    # calculate distance
    top_tracks_distances = np.sqrt(((top_tracks - user_top_tracks) ** 2).sum(axis=1) / len(user_top_tracks))

    # map each distance to a user id
    top_tracks_distances_df = pd.DataFrame(top_tracks_distances, columns=['top_tracks_distance'])
    top_tracks_distances_df['user_id'] = top_tracks_df['user_id']
    
    return top_tracks_distances_df


def calculate_top_artists_distance(username, top_artists_df):
    # get user features
    last_fm = lastfm_api('/Users/ziandong/TreeMusicRecommendation/Data/conf.json')
    user_feature = last_fm.get_user_features(username)
    user_feature['top_artists'] = calculate_top_artists_score(user_feature['top_artists'])

    # convert user features to vector
    # top artist vector
    top_artist_ids = top_artists_df.columns[top_artists_df.columns != "user_id"]
    top_artists_map = {artist_id: idx for idx, artist_id in enumerate(top_artist_ids)}
    user_top_artists = np.zeros(len(top_artist_ids))
    for artist_id  in user_feature['top_artists']:
        if artist_id in top_artists_map:
            user_top_artists[top_artists_map[artist_id]] = user_feature['top_artists'][artist_id]
    
    # convert database user features to model input arrays
    top_artists = top_artists_df.drop(columns=['user_id']).values

    # calculate distance
    top_artists_distances = np.sqrt(((top_artists - user_top_artists) ** 2).sum(axis=1) / len(user_top_artists))

    # map each distance to a user id
    top_artists_distances_df = pd.DataFrame(top_artists_distances, columns=['top_artists_distance'])
    top_artists_distances_df['user_id'] = top_artists_df['user_id']

    return top_artists_distances_df


def calculate_top_tags_distance(username, top_tags_df):
    # get user features
    last_fm = lastfm_api('/Users/ziandong/TreeMusicRecommendation/Data/conf.json')
    user_feature = last_fm.get_user_features(username)
    user_tags = fetch_user_tag(urls_to_text(list(user_feature['top_artists'].keys())[0:10]))
    user_tags = user_tags.split(', ')
    user_feature['top_tags'] = {tag.split(": ")[0].replace('"', ''): float(tag.split(": ")[1].replace('"', '')) for tag in user_tags}

    # convert user features to vector
    # top tag vector
    top_tag_ids = top_tags_df.columns[top_tags_df.columns != "user_id"]
    top_tags_map = {tag: idx for idx, tag in enumerate(top_tag_ids)}
    user_top_tags = np.zeros(len(top_tag_ids))
    for tag  in user_feature['top_tags']:
        if tag in top_tags_map:
            user_top_tags[top_tags_map[tag]] = user_feature['top_tags'][tag]

    # convert database user features to model input arrays
    top_tags = top_tags_df.drop(columns=['user_id']).values

    # calculate distance
    top_tags_distances = np.sqrt(((top_tags - user_top_tags) ** 2).sum(axis=1)/len(user_top_tags))


    # map each distance to a user id
    top_tags_distances_df = pd.DataFrame(top_tags_distances, columns=['top_tags_distance'])
    top_tags_distances_df['user_id'] = top_tags_df['user_id']

    return top_tags_distances_df


def calculate_user_distance(username, top_tracks_df, top_artists_df, top_tags_df):
    top_tracks_distances_df = calculate_top_tracks_distance(username, top_tracks_df)
    top_artists_distances_df = calculate_top_artists_distance(username, top_artists_df)
    top_tags_distances_df = calculate_top_tags_distance(username, top_tags_df)

    # merge all distances
    distances_df = top_tracks_distances_df.merge(top_artists_distances_df, on='user_id')
    distances_df = distances_df.merge(top_tags_distances_df, on='user_id')

    # calculate total distance
    distances_df['distance'] = distances_df['top_tags_distance'] + distances_df['top_artists_distance'] + distances_df['top_tracks_distance']

    # sort by distance
    distances_df = distances_df.sort_values(by=['distance'])

    return distances_df



top_tracks_df = concatenate_feature_csvs("Top Tracks")
top_tracks_df = top_tracks_df.fillna(0)

top_artists_df = concatenate_feature_csvs("Top Artists")
top_artists_df = top_artists_df.fillna(0)

top_tags_df = concatenate_feature_csvs("Top Tags")
top_tags_df = top_tags_df.fillna(0)


def main():
    distances_df = calculate_user_distance("Thiagotake", top_tracks_df, top_artists_df, top_tags_df)

    return distances_df



if __name__ == "__main__":
    distances_df = main()
    print(distances_df.head(10))