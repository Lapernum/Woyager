"""API Methods for fetching data from database and Last.fm API"""

def fetch_all_users(conn):
    """
    Fetches all users from the database
    :param conn: database connection
    :return: list of user ids
    """
    query = "SELECT user_id FROM Users;"
    with conn.cursor() as cur:
        cur.execute(query)
        return [row[0] for row in cur.fetchall()]