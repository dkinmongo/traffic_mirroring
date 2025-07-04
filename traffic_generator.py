import requests
import json
import time
import random
from faker import Faker
# from bson.objectid import ObjectId  <- 삭제

# Nginx proxy server address
NGINX_URL = "http://127.0.0.1"

# Create a Faker instance
fake = Faker()

# --- Functions for /data endpoint ---

def create_user():
    """Creates new user data with a client-generated ID and sends a POST request."""
    user_id = fake.uuid4()  # << 수정: faker로 임의의 UUID 생성
    user_data = {
        "_id": user_id,
        "name": fake.name(),
        "city": fake.city(),
        "email": fake.email()
    }
    try:
        print(f"\n[POST] /data | Attempting to create user: {user_data['name']} with ID: {user_id}")
        response = requests.post(f"{NGINX_URL}/data", json=user_data)
        response.raise_for_status()
        print(f"Success: {response.status_code} | Response: {response.json()}")
        return user_id
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")
        return None

# update_user, get_user, get_all_users 함수는 기존과 동일합니다.
def update_user(user_id):
    if not user_id:
        print("\n[PUT] /data/{id} | No user ID provided for update.")
        return
    new_city = fake.city()
    try:
        print(f"\n[PUT] /data/{user_id} | Attempting to update city info: {new_city}")
        response = requests.put(f"{NGINX_URL}/data/{user_id}", json={"city": new_city})
        response.raise_for_status()
        print(f"Success: {response.status_code} | Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")

def get_user(user_id):
    if not user_id:
        print("\n[GET] /data/{id} | No user ID provided for retrieval.")
        return
    try:
        print(f"\n[GET] /data/{user_id} | Attempting to retrieve user info")
        response = requests.get(f"{NGINX_URL}/data/{user_id}")
        response.raise_for_status()
        print(f"Success: {response.status_code} | Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")

def get_all_users():
    try:
        print("\n[GET] /data | Attempting to retrieve all users")
        response = requests.get(f"{NGINX_URL}/data")
        response.raise_for_status()
        user_count = len(response.json())
        print(f"Success: {response.status_code} | Retrieved {user_count} users in total from /data")
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")


# --- NEW Functions for /data2 endpoint ---

def create_user2():
    """Creates new user data with a client-generated ID and sends a POST request."""
    user_id = fake.uuid4()  # << 수정: faker로 임의의 UUID 생성
    user_data = {
        "_id": user_id,
        "name": fake.name(),
        "job": fake.job(),
        "address": fake.address().replace('\n', ', ')
    }
    try:
        print(f"\n[POST] /data2 | Attempting to create user: {user_data['name']} with ID: {user_id}")
        response = requests.post(f"{NGINX_URL}/data2", json=user_data)
        response.raise_for_status()
        print(f"Success: {response.status_code} | Response: {response.json()}")
        return user_id
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")
        return None

# update_user2, get_user2, get_all_users2 함수는 기존과 동일합니다.
def update_user2(user_id):
    if not user_id:
        print("\n[PUT] /data2/{id} | No user ID provided for update.")
        return
    new_job = fake.job()
    try:
        print(f"\n[PUT] /data2/{user_id} | Attempting to update job info: {new_job}")
        response = requests.put(f"{NGINX_URL}/data2/{user_id}", json={"job": new_job})
        response.raise_for_status()
        print(f"Success: {response.status_code} | Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")

def get_user2(user_id):
    if not user_id:
        print("\n[GET] /data2/{id} | No user ID provided for retrieval.")
        return
    try:
        print(f"\n[GET] /data2/{user_id} | Attempting to retrieve user info")
        response = requests.get(f"{NGINX_URL}/data2/{user_id}")
        response.raise_for_status()
        print(f"Success: {response.status_code} | Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")

def get_all_users2():
    try:
        print("\n[GET] /data2 | Attempting to retrieve all users")
        response = requests.get(f"{NGINX_URL}/data2")
        response.raise_for_status()
        user_count = len(response.json())
        print(f"Success: {response.status_code} | Retrieved {user_count} users in total from /data2")
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")


# main 실행 부분은 기존과 동일합니다.
if __name__ == "__main__":
    print("--- Starting traffic generation ---")

    # --- Test /data endpoint ---
    print("\n" + "="*20 + " Testing /data endpoint " + "="*20)
    created_user_ids_1 = []
    for _ in range(2): # Create 2 new users
        new_id = create_user()
        if new_id:
            created_user_ids_1.append(new_id)
        time.sleep(1)

    if created_user_ids_1:
        user_to_update = random.choice(created_user_ids_1)
        update_user(user_to_update)
        time.sleep(1)
        get_user(user_to_update)
        time.sleep(1)
    get_all_users()

    # --- Test /data2 endpoint ---
    print("\n" + "="*20 + " Testing /data2 endpoint " + "="*20)
    created_user_ids_2 = []
    for _ in range(2): # Create 2 new users
        new_id = create_user2()
        if new_id:
            created_user_ids_2.append(new_id)
        time.sleep(1)

    if created_user_ids_2:
        user_to_update = random.choice(created_user_ids_2)
        update_user2(user_to_update)
        time.sleep(1)
        get_user2(user_to_update)
        time.sleep(1)
    get_all_users2()

    print("\n--- Traffic generation complete ---")
