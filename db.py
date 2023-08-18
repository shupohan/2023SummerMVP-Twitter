import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")


class user:
    def __init__(self):
        self.connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD,
        )

    def insert(self, name, total_followers):
        cursor = self.connection.cursor()

        name = name
        total_followers = total_followers

        insert_query = """
        INSERT INTO users (username, followers)
        VALUES (%s, %s);
        """

        data_to_insert = (name, total_followers)
        try:
            cursor.execute(insert_query, data_to_insert)
        except Exception as e:
            print(f"{e}")

        self.connection.commit()
        cursor.close()

    def get_all_users(self):
        cursor = self.connection.cursor()

        query = """
        Select id, username FROM users;
        """

        try:
            cursor.execute(query)
        except Exception as e:
            print(f"{e}")

        all_users = cursor.fetchall()

        self.connection.commit()
        cursor.close()

        return all_users

    def __del__(self):
        self.connection.close()


class tweet:
    def __init__(self):
        self.connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD,
        )

    def get_user_id(self, name):
        cursor = self.connection.cursor()
        query = "SELECT id FROM users WHERE username = %s;"
        cursor.execute(query, (name,))
        user_id = cursor.fetchone()[0]

        self.connection.commit()
        cursor.close()

        return user_id

    def insert(self, user_id, replies, retweets, likes, views, event_time):
        cursor = self.connection.cursor()

        insert_query = """
        INSERT INTO tweets (user_id, replies, retweets, likes, views, event_time)
        VALUES (%s, %s, %s, %s, %s, %s);
        """

        event_time = self.transform_timestamps(event_time)

        data_to_insert = (user_id, replies, retweets, likes, views, event_time)
        try:
            cursor.execute(insert_query, data_to_insert)
        except Exception as e:
            print(f"{e}")

        self.connection.commit()
        cursor.close()

    def transform_timestamps(self, timestamp):
        try:
            # Parse the input timestamp string to a Python datetime object
            datetime_object = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

            # Format the datetime object as per the desired format 'YYYY-MM-DD HH:MI:SS.MS+00:00'
            formatted_timestamp = datetime_object.strftime("%Y-%m-%d %H:%M:%S.%f+00:00")
        except ValueError:
            print(f"Error: Unable to parse the timestamp '{timestamp}'")

        return formatted_timestamp

    def get_all_tweets(self, user_id):
        cursor = self.connection.cursor()

        query = """
        Select * FROM tweets WHERE user_id = %s;
        """

        try:
            cursor.execute(query, (user_id,))
        except Exception as e:
            print(f"{e}")

        all_tweets = cursor.fetchall()

        self.connection.commit()
        cursor.close()

        return all_tweets

    def __del__(self):
        self.connection.close()
