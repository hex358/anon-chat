import json
import os
import hashlib
from pymongo import MongoClient

# ---------------------------
# Setup MongoDB connection
# ---------------------------
client = MongoClient('mongodb://localhost:27017/')
db = client['anon_chat']
users = db["users"]
userchats = db["chats"]
cache = db["cache"]

# ---------------------------
# Utility: SHA-256 hashing
# ---------------------------
def hash_id(identifier):
    """
    Compute a SHA-256 hash of the given identifier (str or int)
    and return its hexadecimal representation.
    """
    raw = str(identifier).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

# ---------------------------
# General-purpose upload
# ---------------------------
def upload(collection, content):
    """
    Insert a document into the specified collection.
    If inserting into the 'users' collection and an 'orig' field
    is present, immediately hash that value so we never store the plain ID.
    """
    if collection == users and "orig" in content:
        # Replace plain-text user ID with its SHA-256 hash
        content["orig"] = hash_id(content["orig"])
    collection.insert_one(content)

# ---------------------------
# Generic key retrieval / update
# ---------------------------
def key(collection, location, to_get):
    """
    Fetch a single field (to_get) from the first document matching 'location'.
    """
    return collection.find_one(location)[to_get]

def set_key(collection, location, new_values: dict):
    """
    Update fields in a document matching 'location' with the entries in new_values.
    """
    filter_criteria = location
    updated = {"$set": new_values}
    collection.update_one(filter_criteria, updated)

# ---------------------------
# User-specific helpers (with hashing)
# ---------------------------
def set_user_key(user, new_values: dict):
    """
    Given a plain user ID, hash it and update the corresponding document
    in the 'users' collection with new_values.
    """
    hashed = hash_id(user)
    filter_criteria = {"orig": hashed}
    updated = {"$set": new_values}
    users.update_one(filter_criteria, updated)

def get_user_key(user, to_get):
    """
    Given a plain user ID, hash it and retrieve the requested field from that user's document.
    """
    hashed = hash_id(user)
    doc = users.find_one({"orig": hashed})
    return doc[to_get] if doc else None

def locate_user(orig_id):
    """
    Find and return the entire user document for the given plain user ID (after hashing).
    """
    hashed = hash_id(orig_id)
    return users.find_one({"orig": hashed})

# ---------------------------
# Chat-specific helpers
# ---------------------------
def get_chat_key(chat, to_get):
    """
    Retrieve a single field (to_get) from the chat's document.
    The 'name' field is assumed to be the unique identifier for a chat.
    """
    return userchats.find_one({"name": str(chat)})[to_get]

def set_chat_key(chat, new_values: dict):
    """
    Update the chat document (matched by name) with new_values.
    """
    filter_criteria = {"name": chat}
    updated = {"$set": new_values}
    userchats.update_one(filter_criteria, updated)

def locate_chat(name_id):
    """
    Find and return the entire chat document by its name.
    """
    return userchats.find_one({"name": name_id})

# ---------------------------
# Cache-specific helpers
# ---------------------------
def update_cached(id, type, new_values: dict):
    """
    Update the cache document (matched by id and type) with new_values.
    """
    filter_criteria = {"id": id, "type": type}
    updated = {"$set": new_values}
    cache.update_one(filter_criteria, updated)

def create_cached(id, type, user, start_set, ids=None):
    """
    Create a new cache document if one does not already exist for (id, type).
    If it exists, overwrite its 'content' and 'ids' fields.
    """
    filter_criteria = {"id": id, "type": type}
    found = cache.find_one(filter_criteria)
    if found:
        # Overwrite content and ids
        cache.update_one(filter_criteria, {"$set": {"content": start_set, "ids": ids}})
        return 0
    cache.insert_one({"id": id, "type": type, "user": user, "content": start_set, "ids": ids})

def get_cached(id, type, to_get):
    """
    Retrieve a single field (to_get) from the cache document matched by (id, type).
    """
    return cache.find_one({"id": id, "type": type})[to_get]

# ---------------------------
# Generic delete / append helpers
# ---------------------------
def delete_key(collection, filter_criteria):
    """
    Delete a single document matching filter_criteria from the given collection.
    """
    return collection.delete_one(filter_criteria)

def append_key(collection, location, to_set: dict):
    """
    Append a value to an existing list field in a document.
    'to_set' should be a dict with exactly one key mapping to a single new element.
    Example: to_set = {"friends": "new_friend_id"}
    """
    keys = list(to_set.keys())
    field_name = keys[0]
    existing_list = key(collection, location, field_name)
    existing_list.append(to_set[field_name])
    set_key(collection, location, {field_name: existing_list})
    return existing_list
