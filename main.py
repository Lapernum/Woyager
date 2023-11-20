import sys
sys.path.append('.')


from backend.user.calculation import *
from flask import Flask, jsonify
import pandas as pd
from flask import render_template



app = Flask(__name__)

#top_tags_df = concatenate_feature_csvs("Top Tags")
#top_tags_df = top_tags_df.fillna(0)
#print(1)

#top_artists_df = concatenate_feature_csvs("Top Artists")
#top_artists_df = top_artists_df.fillna(0)
#print(2)

#top_tracks_df = concatenate_feature_csvs("Top Tracks")
#print(2)
#top_tracks_df = top_tracks_df.fillna(0)
#print(3)

top_tags_df = pd.read_csv('backend/user/user_features/Top Tags_0.csv')
top_tags_df = top_tags_df.fillna(0)

top_artists_df = pd.read_csv('backend/user/user_features/Top Artists_0.csv')
top_artists_df = top_artists_df.fillna(0)

top_tracks_df = pd.read_csv('backend/user/user_features/Top Tracks_0.csv')
top_tracks_df = top_tracks_df.fillna(0)


explored_user = set()
explored_user.add('miranta8') #start user



def calculate(username):
    df = calculate_user_distance(username, top_tracks_df, top_artists_df, top_tags_df)
    #drop row with explored user
    df = df[~df['username'].isin(explored_user)][0:10]

    json_data = df.to_json(orient='records')

    # append usernames in df to explored user
    explored_user.update(df['username'].tolist())
    
    return json_data

@app.route('/') #hard code first
def index():
    return render_template('/similar_users/index.html')

@app.route('/get_data/<username>')
def get_data(username):
    data = calculate(username)  
    return jsonify(data)






