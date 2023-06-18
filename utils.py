from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pysentimiento import create_analyzer
import bcrypt

from dotenv import load_dotenv
import os

dotenv_path = '.env'
load_dotenv(dotenv_path)

USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.jymugtw.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri, server_api=ServerApi('1'))

db = client.mapproject

users = db['users']
messages = db['messages']

analyser = create_analyzer(task="hate_speech", lang="en")


def create_user(username, password):
    user_obj = {"username": username,
                "password": password}

    if check_user(username):
        return False
    users_id = users.insert_one(user_obj).inserted_id
    return users_id


def login_user(username, password):
    user_obj = users.find_one({"username": username})
    return bcrypt.checkpw(str.encode(password), user_obj["password"])


def check_user(username):
    if users.find_one({"username": username}):
        return True
    return False


def check_words(text):
    results = analyser.predict(text)
    return results


def add_message(message_obj):
    results = check_words(message_obj['text'])
    if not results.output:
        message_id = messages.insert_one(message_obj).inserted_id
        return message_id
    return False