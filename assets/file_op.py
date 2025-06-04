import json
import os
import hashlib
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['anon_chat']
users = db["users"]
userchats = db["chats"]
cache = db["cache"]

def hash_id(identifier):
    raw = str(identifier).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

def upload(collection, content):
    if collection == users and "orig" in content:
        content["orig"] = hash_id(content["orig"])
    collection.insert_one(content)

def key(collection, location, to_get):
    return collection.find_one(location)[to_get]

def set_key(collection, location, new_values: dict):
    filter_criteria = location
    updated = {"$set": new_values}
    collection.update_one(filter_criteria, updated)

def set_user_key(user, new_values: dict):
    hashed = hash_id(user)
    filter_criteria = {"orig": hashed}
    updated = {"$set": new_values}
    users.update_one(filter_criteria, updated)

def get_user_key(user, to_get):
    hashed = hash_id(user)
    doc = users.find_one({"orig": hashed})
    return doc[to_get] if doc else None

def locate_user(orig_id):
    hashed = hash_id(orig_id)
    return users.find_one({"orig": hashed})

def get_chat_key(chat, to_get):
    return userchats.find_one({"name": str(chat)})[to_get]

def set_chat_key(chat, new_values: dict):
    filter_criteria = {"name": chat}
    updated = {"$set": new_values}
    userchats.update_one(filter_criteria, updated)

def locate_chat(name_id):
    return userchats.find_one({"name": name_id})

def update_cached(id, type, new_values: dict):
    filter_criteria = {"id": id, "type": type}
    updated = {"$set": new_values}
    cache.update_one(filter_criteria, updated)

def create_cached(id, type, user, start_set, ids=None):
    filter_criteria = {"id": id, "type": type}
    found = cache.find_one(filter_criteria)
    if found:
        cache.update_one(filter_criteria, {"$set": {"content": start_set, "ids": ids}})
        return 0
    cache.insert_one({"id": id, "type": type, "user": user, "content": start_set, "ids": ids})

def get_cached(id, type, to_get):
    return cache.find_one({"id": id, "type": type})[to_get]

def delete_key(collection, filter_criteria):
    return collection.delete_one(filter_criteria)

def append_key(collection, location, to_set: dict):
    keys = list(to_set.keys())
    field_name = keys[0]
    existing_list = key(collection, location, field_name)
    existing_list.append(to_set[field_name])
    set_key(collection, location, {field_name: existing_list})
    return existing_list
