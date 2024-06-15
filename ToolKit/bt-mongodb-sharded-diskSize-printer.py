import pymongo
import argparse

def get_connection_info():
    parser = argparse.ArgumentParser(description='Connect to MongoDB and list databases and collection sizes.')
    parser.add_argument('--user', type=str, help='MongoDB user', default=None)
    parser.add_argument('--password', type=str, help='MongoDB password', default=None)
    parser.add_argument('--host', type=str, help='MongoDB host', default='localhost')
    parser.add_argument('--port', type=int, help='MongoDB port', default=27017)
    args = parser.parse_args()
    return args

def list_databases_and_collections(client):
    db_list = client.list_database_names()
    for db_name in db_list:
        db = client[db_name]
        print(f"Database: {db_name}")
        colls = db.list_collection_names()
        for coll_name in colls:
            coll = db[coll_name]
            coll_stats = db.command("collStats", coll_name)
            document_count = coll_stats.get('count', 0)
            storage_size = coll_stats.get('size', 0)
            print(f"  Collection: {coll_name}, Size: {document_count} documents, Storage Size: {storage_size} bytes")

def main():
    args = get_connection_info()
    user = args.user
    password = args.password
    host = args.host
    port = args.port

    if user and password:
        uri = f"mongodb://{user}:{password}@{host}:{port}/"
    else:
        uri = f"mongodb://{host}:{port}/"

    client = pymongo.MongoClient(uri)

    # Ensure we are connected to a sharded environment
    config_db = client['config']
    shards_collection = config_db['shards']
    if shards_collection.count_documents({}) == 0:
        print("This is not a sharded environment.")
        return

    list_databases_and_collections(client)

if __name__ == '__main__':
    main()
