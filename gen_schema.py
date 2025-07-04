import pymongo
import json
from datetime import datetime

# ## CONFIGURATION ##
# ##############################################################################

# Schema extraction source MongoDB information
SOURCE_MONGO_URI = "mongodb://user:password@host1:27017,host2:27017,host3:27017/?replicaSet=rs0"

# Name for the generated JavaScript file
OUTPUT_JS_FILE = "apply_all_schemas.js"

# List of databases to exclude from schema extraction
EXCLUDED_DBS = ['admin', 'config', 'local']

# ##############################################################################


def get_collections(db, file):
    """Generates creation scripts for all collections."""
    file.write("\n// 1. Collections\n")
    try:
        for coll_info in db.list_collections():
            coll_name = coll_info['name']
            if coll_name.startswith('system.'):
                continue

            options = coll_info.get('options', {})

            if options:
                options.pop('uuid', None)
                options_str = json.dumps(options)
                file.write(f'db.createCollection("{coll_name}", {options_str});\n')
            else:
                file.write(f'db.createCollection("{coll_name}");\n')

    except Exception as e:
        file.write(f"// Error fetching collection info for DB '{db.name}': {e}\n")

def clean_index_options(options):
    """Cleans index options for the createIndex command."""
    valid_options = options.copy()
    for key in ['v', 'ns', 'key', 'uuid']:
        if key in valid_options:
            del valid_options[key]
    return valid_options

def get_indexes(db, file):
    """Generates creation scripts for all indexes."""
    file.write("\n// 2. Indexes\n")
    for coll_name in db.list_collection_names():
        if coll_name.startswith('system.'):
            continue
        try:
            for index in db[coll_name].list_indexes():
                if index['name'] == '_id_':
                    continue
                
                keys_str = json.dumps(dict(index['key']))
                options_str = json.dumps(clean_index_options(index))
                
                file.write(f'db.getCollection("{coll_name}").createIndex({keys_str}, {options_str});\n')
        except Exception as e:
            file.write(f"// Error fetching indexes for '{db.name}.{coll_name}': {e}\n")


def get_views(db, file):
    """Generates creation scripts for all views."""
    file.write("\n// 3. Views\n")
    try:
        for coll_info in db.list_collections():
            if coll_info['type'] == 'view':
                view_name = coll_info['name']
                options = coll_info.get('options', {})
                view_on = options.get('viewOn')
                pipeline = options.get('pipeline')
                
                if not view_on or not pipeline:
                    continue

                pipeline_str = json.dumps(pipeline)
                file.write(f'db.createView("{view_name}", "{view_on}", {pipeline_str});\n')
    except Exception as e:
        file.write(f"// Error fetching view info for DB '{db.name}': {e}\n")

def get_users(db, file):
    """Generates creation scripts for database users."""
    file.write("\n// 4. Users\n")
    file.write("// IMPORTANT: Replace 'PLEASE_SET_PASSWORD' with a real password before running.\n")

    try:
        users_info = db.command('usersInfo')['users']
        if not users_info:
            return
            
        for user in users_info:
            clean_roles = []
            for role in user['roles']:
                if role['role'].startswith('__'): # Skip internal roles
                    continue
                role.pop('minFcv', None)
                clean_roles.append(role)

            user_doc = {"user": user['user'], "pwd": "PLEASE_SET_PASSWORD", "roles": clean_roles}
            user_doc_str = json.dumps(user_doc)
            
            file.write(f"db.createUser({user_doc_str});\n")
            
    except Exception as e:
        file.write(f"// Could not retrieve users for DB '{db.name}'. Error: {e}\n")

def main():
    """Main execution function."""
    print(f"Connecting to MongoDB...")
    try:
        client = pymongo.MongoClient(SOURCE_MONGO_URI)
        client.admin.command('ping')
    except Exception as e:
        print(f"Error: Could not connect to MongoDB. {e}")
        return

    try:
        db_names = client.list_database_names()
        user_dbs = [db_name for db_name in db_names if db_name not in EXCLUDED_DBS]
        print(f"Found user databases to process: {user_dbs}")
    except Exception as e:
        print(f"Error: Could not list databases. {e}")
        client.close()
        return

    with open(OUTPUT_JS_FILE, 'w', encoding='utf-8') as f:
        f.write(f"// MongoDB Schema Script - Generated on: {datetime.now().isoformat()}\n")

        # Process schemas for each user database
        for db_name in user_dbs:
            print(f"  Processing database: '{db_name}'...")
            db = client[db_name]

            f.write(f"\n// --- Schema for database: {db_name} ---\n")
            f.write(f'use("{db_name}");\n')

            get_collections(db, f)
            get_indexes(db, f)
            get_views(db, f)
            get_users(db, f)

        # Special handling for users in the 'admin' database
        print("  Processing users from 'admin' database...")
        admin_db = client['admin']
        f.write(f"\n// --- Users defined in 'admin' database ---\n")
        f.write('use("admin");\n')
        get_users(admin_db, f)


    client.close()
    print(f"\n✅ Successfully generated schema script: '{OUTPUT_JS_FILE}'")
    print("🚨 IMPORTANT: Remember to manually set passwords in the generated script!")

if __name__ == "__main__":
    main()
