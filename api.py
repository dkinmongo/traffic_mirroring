# main.py
import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
# from bson.objectid import ObjectId  <- 더 이상 필요 없으므로 주석 처리하거나 삭제
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:Manager1@10.0.1.251:30000,10.0.1.184:30000,10.0.1.167:30000/?replicaSet=restore")
DB_NAME = "dual"

try:
    # Create MongoDB client
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    # Define two separate collections for the different endpoints
    collection = db.mycollection
    collection2 = db.mycollection2
    # Test connection
    client.server_info()
    print("✅ Successfully connected to MongoDB.")

except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    client = None

# --- API Endpoints for /data (mycollection) ---

@app.route('/data', methods=['POST'])
def add_data():
    """Adds a new document to mycollection."""
    if not client:
        return jsonify({"error": "Database connection not available."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Valid JSON data is required."}), 400

        # 클라이언트가 제공한 _id를 그대로 사용합니다.
        if '_id' not in data:
            return jsonify({"error": "_id is required."}), 400

        result = collection.insert_one(data)
        inserted_id = data['_id'] # 서버에서 생성하는 대신 클라이언트가 제공한 ID를 사용
        print(f"✅ [Collection 1] Data insertion successful: {inserted_id}")

        return jsonify({
            "message": "Data added successfully to mycollection.",
            "inserted_id": str(inserted_id)
        }), 201

    except Exception as e:
        print(f"❌ [Collection 1] Data insertion failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/data/<string:id>', methods=['PUT'])
def update_data(id):
    """Updates an existing document in mycollection by its string ID."""
    if not client:
        return jsonify({"error": "Database connection not available."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Valid JSON data is required."}), 400

        # 📍 수정: ObjectId() 변환을 제거하고 문자열 ID를 직접 사용
        result = collection.update_one({'_id': id}, {'$set': data})

        if result.matched_count == 0:
            return jsonify({"error": "Document with the given ID not found."}), 404

        print(f"✅ [Collection 1] Data update successful: {id}")
        return jsonify({"message": f"Document (id: {id}) updated successfully in mycollection."}), 200

    except Exception as e:
        print(f"❌ [Collection 1] Data update failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/data/<string:id>', methods=['GET'])
def get_data_by_id(id):
    """Retrieves a specific document from mycollection by its string ID."""
    if not client:
        return jsonify({"error": "Database connection not available."}), 500
    try:
        # 📍 수정: ObjectId() 변환을 제거하고 문자열 ID를 직접 사용
        document = collection.find_one({'_id': id})

        if document:
            # _id는 이미 문자열이므로 변환이 필요 없습니다.
            return jsonify(document), 200
        else:
            return jsonify({"error": "Data not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/data', methods=['GET'])
def get_all_data():
    """Retrieves all documents from mycollection."""
    if not client:
        return jsonify({"error": "Database connection not available."}), 500
    try:
        documents = []
        for doc in collection.find():
            # _id는 이미 문자열이므로 변환이 필요 없습니다.
            documents.append(doc)
        return jsonify(documents), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- NEW API Endpoints for /data2 (mycollection2) ---

@app.route('/data2', methods=['POST'])
def add_data2():
    """Adds a new document to mycollection2."""
    if not client:
        return jsonify({"error": "Database connection not available."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Valid JSON data is required."}), 400

        if '_id' not in data:
            return jsonify({"error": "_id is required."}), 400

        result = collection2.insert_one(data)
        inserted_id = data['_id']
        print(f"✅ [Collection 2] Data insertion successful: {inserted_id}")

        return jsonify({
            "message": "Data added successfully to mycollection2.",
            "inserted_id": str(inserted_id)
        }), 201

    except Exception as e:
        print(f"❌ [Collection 2] Data insertion failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/data2/<string:id>', methods=['PUT'])
def update_data2(id):
    """Updates an existing document in mycollection2 by its string ID."""
    if not client:
        return jsonify({"error": "Database connection not available."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Valid JSON data is required."}), 400

        # 📍 수정: ObjectId() 변환을 제거하고 문자열 ID를 직접 사용
        result = collection2.update_one({'_id': id}, {'$set': data})

        if result.matched_count == 0:
            return jsonify({"error": "Document with the given ID not found."}), 404

        print(f"✅ [Collection 2] Data update successful: {id}")
        return jsonify({"message": f"Document (id: {id}) updated successfully in mycollection2."}), 200

    except Exception as e:
        print(f"❌ [Collection 2] Data update failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/data2/<string:id>', methods=['GET'])
def get_data_by_id2(id):
    """Retrieves a specific document from mycollection2 by its string ID."""
    if not client:
        return jsonify({"error": "Database connection not available."}), 500
    try:
        # 📍 수정: ObjectId() 변환을 제거하고 문자열 ID를 직접 사용
        document = collection2.find_one({'_id': id})

        if document:
            return jsonify(document), 200
        else:
            return jsonify({"error": "Data not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/data2', methods=['GET'])
def get_all_data2():
    """Retrieves all documents from mycollection2."""
    if not client:
        return jsonify({"error": "Database connection not available."}), 500
    try:
        documents = []
        for doc in collection2.find():
            documents.append(doc)
        return jsonify(documents), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
