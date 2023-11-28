import sys
sys.path.append('.')


from backend.user.calculation import *
from backend.song_algorithm import SelfListening
from Data.data_api import *
from flask import Flask, jsonify
import pandas as pd
from flask import render_template



app = Flask(__name__)



top_tags_df = concatenate_feature_csvs("Top Tags")
top_tags_df = top_tags_df.fillna(0)
print(1)

top_artists_df = concatenate_feature_csvs("Top Artists")
top_artists_df = top_artists_df.fillna(0)
print(2)

top_tracks_df = concatenate_feature_csvs("Top Tracks")
top_tracks_df = top_tracks_df.fillna(0)
#print(3)

# top tags_df = pd.read_csv('backend/user/Top Tags_0.csv')
# top artists_df = pd.read_csv('backend/user/Top Artists_0.csv')
# top tracks_df = pd.read_csv('backend/user/Top Tracks_0.csv')
# top tags_df = top tags_df.fillna(0)
# top artists_df = top artists_df.fillna(0)
# top tracks_df = top tracks_df.fillna(0)




explored_user = set()
explored_user.add(1) #start user

last_fm = lastfm_api('D:/CSE6242/TreeMusicRecommendation/Data/conf.json')


def calculate(username):
    df = calculate_user_distance(username, top_tracks_df, top_artists_df, top_tags_df, explored_user)
    #drop row with explored user

    json_data = df.to_json(orient='records')

    # append usernames in df to explored user
    explored_user.update(df['user_id'].tolist())
    
    return json_data

@app.route('/') #hard code first
def index():
    return render_template('/index.html')

@app.route('/similar_user/<username>') #hard code first
def similar_user_index(username):
    return render_template('/similar_users/index.html', username=username)

@app.route('/get_data/<username>')
def get_data(username):
    data = calculate(username)  
    return jsonify(data)

@app.route('/clear_explored_users', methods=['POST']) #hard code first
def clear_explored_users():
    explored_user.clear()
    explored_user.add(1) # add start user
    return jsonify({'status': 'success'}), 200

@app.route('/')
def login():
    return render_template('/login.html')

user = None

@app.route('/self_listening/<username>')
def provide_targets(username):
    '''
    Function to retrieve user name from login,
    then return the target tags and top artists for choosing
    '''
    global user
    user = SelfListening(username)
    return jsonify(user.get_target())

@app.route('/self_listening/<username>/<choice>')
def recommend_songs(username, choice):
    '''
    The user will select a choice from targets,
    this function recommend 10 songs
    '''
    global user
    user.change_mode(choice)
    ten_songs, scores = user.select_ten()
    return jsonify(ten_songs, scores)

@app.route('/self_listening/<username>/add_track/<track>')
def add_track(username, track):
    '''
    The user will select a song from the 10 songs,
    this function add this selected song to the corresponding SelfListening class object

    track: {'track_name', 'artist_name'}
    '''
    global user
    user.add_track(track)
    # After adding this track, a new(same) set of targets will be posted
    return jsonify(user.get_target())

@app.route('/check_user/<username>')
def check_user(username):
    data = last_fm.get_user_image_url(username)
    if data is None:
        return jsonify(False)
    else:
        return jsonify(True)
    
@app.route('/get_user_image/<username>')
def get_user_image(username):
    data = last_fm.get_user_image_url(username)
    return jsonify(data)


if __name__ == '__main__':
    app.run(port=5500)








