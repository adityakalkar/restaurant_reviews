from datetime import datetime
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests

# Load environment variables
load_dotenv()

# MongoDB connection
DB_PASSWORD = os.getenv('DB_PASSWORD')
client = MongoClient(f'mongodb+srv://adityakalkar07:{DB_PASSWORD}@cluster0.5xz4b.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

# Use the restaurantDb database
db = client['restaurantDb']

# Collections
users = db['users']
reviews = db['reviews']

# Yelp API Key
YELP_API_KEY = os.getenv('YELP_API_KEY')

def create_user(username, email, hashed_password):
    """Insert a new user into the database."""
    return users.insert_one({
        'username': username,
        'email': email,
        'password': hashed_password
    })

def find_user_by_email(email):
    """Find a user by email."""
    return users.find_one({'email': email})

def find_user_by_id(user_id):
    """Find a user by ID."""
    return users.find_one({'_id': ObjectId(user_id)})



def create_review(restaurant_name, rating, comment, user_id, username):
    """Insert a new review into the database."""
    return reviews.insert_one({
        'restaurant_name': restaurant_name,
        'rating': rating,
        'comment': comment,
        'user_id': user_id,
        'username': username,
        'timestamp': datetime.utcnow()
    })


def get_all_reviews():
    return reviews.find().sort('timestamp', -1)

def get_reviews_by_user(user_id):
    return reviews.find({'user_id': user_id}).sort('timestamp', -1)  

def find_review_by_id(review_id):
    return reviews.find_one({'_id': ObjectId(review_id)})

def update_review(review_id, rating, comment):
    return reviews.update_one(
        {'_id': ObjectId(review_id)},
        {'$set': {'rating': rating, 'comment': comment, 'timestamp': datetime.utcnow()}}
    )

def delete_review(review_id):
    return reviews.delete_one({'_id': ObjectId(review_id)})



def search_restaurants(term, location, limit=10):
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {
        "Authorization": f"Bearer {YELP_API_KEY}"
    }
    params = {
        "term": term,       
        "location": location, 
        "limit": limit     
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('businesses', [])  
    else:
        print(f"Error: {response.status_code}, {response.text}") 
        return []