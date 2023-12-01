import sys
sys.path.append('.')


from backend.user.calculation import *
from backend.song_algorithm import SelfListening
from Data.data_api import *
from flask import Flask, jsonify
import pandas as pd
from flask import render_template
from urllib.parse import unquote
import copy
from flask import Flask, jsonify, session, request # Import session

def log_system_usage():
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().used
    print(f'CPU usage: {cpu_usage}%')
    print(f'Memory usage: {memory_usage / (1024.0 ** 3)} GB')  # Convert to GB

app = Flask(__name__)
app.secret_key = 'your secret key'  # Initialize the secret key


last_fm = lastfm_api('./Data/conf.json')
database = database_api('./Data/conf.json')

top_tags_df = concatenate_feature_csvs("Top Tags")
top_tags_df = top_tags_df.fillna(0)
print(1)

top_artists_df = concatenate_feature_csvs("Top Artists")
top_artists_df = top_artists_df.fillna(0)
print(2)

top_tracks_df = concatenate_feature_csvs("Top Tracks")
top_tracks_df = top_tracks_df.fillna(0)
print(3)

explored_user = set()
user_id = None


def calculate(username):
    try:
        # Use session to store explored_user
        explored_user = session.get('explored_user')
        print(explored_user)               
        df = calculate_user_distance(username, top_tracks_df, top_artists_df, top_tags_df, explored_user)
        #drop row with explored user

        json_data = df.to_json(orient='records')

        # append usernames in df to explored user
        explored_user.extend(df['user_id'].tolist())
        session['explored_user'] = explored_user  # Save explored_user back to session
    
        return json_data
    except Exception as e:
        print(e)
        return None


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

@app.route('/clear_explored_users/<username>', methods=['POST']) #hard code first
def clear_explored_users(username):
    user_id = database.get_user_id(username)

    if user_id is not None:
        session['user_id'] = user_id

    session['explored_user'] = []  # Clear explored_user in session
    if user_id is not None:
        session['explored_user'].append(user_id)
    return jsonify({'status': 'success'}), 200

# @app.route('/login')
# def login():
#     return render_template('/login.html')

user = None
primary_target = {}
@app.route('/self_listening/<username>') 
def self_listening_index(username):
    return render_template('/self_listening/index.html', username=username)

@app.route('/targets', methods=['GET'])
def provide_targets():
    '''
    Function to retrieve user name from login,
    then return the target tags and top artists for choosing
    '''
    username = request.args.get('username')
    global user
    global primary_target
    user = SelfListening(unquote(username))
    if user.fail:
        return jsonify(None)
    targets = user.get_target()
    primary_target = targets
    return targets

@app.route('/self_listening/targets', methods=['GET'])
def recommend_songs():
    '''
    The user will select a choice from targets,
    this function recommend 10 songs
    '''
    choice = request.args.get('choice')
    global user
    user.change_mode(unquote(choice))
    ten_songs, scores = user.select_ten()
    scores = scores[:5]
    # apply minimax to scores to map it into (20,40)
    return {"ten_songs": ten_songs[:5], "scores": scores}

@app.route('/self_listening/add_track', methods=['GET'])
def add_track():
    '''
    The user will select a song from the 10 songs,
    this function add this selected song to the corresponding SelfListening class object

    track: {'track_name', 'artist_name'}
    '''
    artist = request.args.get('artist')
    track = request.args.get('track')
    global user
    nt = {'track_name': unquote(track), 'artist_name': unquote(artist)}
    print(nt)
    user.add_track(nt)
    targets = copy.deepcopy(user.get_target())
    print(user.added_track_tag)
    user.update_target(primary_target)
    print(targets)
    # After adding this track, a new(same) set of targets will be posted
    return targets

@app.route('/check_user/<username>')
def check_user(username):
    data = last_fm.get_user_image_url(username)
    user_id = database.get_user_id(username)

    if user_id is not None:
        session['user_id'] = user_id
    
    # Use session to store explored_user
    explored_user = []
    if user_id is not None:
        explored_user.append(user_id)
        session['explored_user'] = explored_user  # Save explored_user back to session
        
    if data is None:
        return jsonify(False)
    else:
        return jsonify(True)
    
@app.route('/get_user_image/<username>')
def get_user_image(username):
    data = last_fm.get_user_image_url(username)
    return jsonify(data)

@app.route('/get_track_image', methods=['GET'])
def get_track_image():
    artist = request.args.get('artist')
    track = request.args.get('track')
    data = last_fm.get_track_image_url(artist, track)
    return jsonify(data)

@app.route('/get_artist_image', methods=['GET'])
def get_artist_image():
    artist = request.args.get('artist')
    data = last_fm.get_artist_image_url(artist)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)








