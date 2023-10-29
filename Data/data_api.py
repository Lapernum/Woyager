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
    
    # Return a list of info json of friends
    def get_user_friends(self, username):
        response = requests.get("https://ws.audioscrobbler.com/2.0/?method=user.getfriends&user= " + username + "&api_key= " + self.api_key + "&format=json")
        data = response.json()
        friends = data["friends"]["user"]
        return friends
    
    # Save all the users provided into the database without replicates
    def save_users(self, users):
        try:
            cnx = mysql.connector.connect(user = self.sql_username, password = self.sql_password, host = self.sql_host, database = self.sql_database)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        
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
        
        return
                    