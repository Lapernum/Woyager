import sys
sys.path.append('.')


from backend.user.calculation import *
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


def calculate(username):
    df = calculate_user_distance(username, top_tracks_df, top_artists_df, top_tags_df, explored_user)
    #drop row with explored user

    json_data = df.to_json(orient='records')

    # append usernames in df to explored user
    explored_user.update(df['user_id'].tolist())
    
    return json_data

@app.route('/') #hard code first
def index():
    return render_template('/similar_users/index.html')

@app.route('/get_data/<username>')
def get_data(username):
    data = calculate(username)  
    return jsonify(data)

@app.route('/clear_explored_users', methods=['POST']) #hard code first
def clear_explored_users():
    explored_user.clear()
    explored_user.add(1) # add start user
    return jsonify({'status': 'success'}), 200





if __name__ == '__main__':
    app.run()








