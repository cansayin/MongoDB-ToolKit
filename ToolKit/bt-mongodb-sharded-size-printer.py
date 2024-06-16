import pymongo
import argparse
from prettytable import PrettyTable
import humanize

def get_connection_info():
    parser = argparse.ArgumentParser(description='Connect to MongoDB and list databases and collection sizes.')
    parser.add_argument('--user', type=str, help='MongoDB user', default=None)
    parser.add_argument('--password', type=str, help='MongoDB password', default=None)
    parser.add_argument('--host', type=str, help='MongoDB host', default='localhost')
    parser.add_argument('--port', type=int, help='MongoDB port', default=27017)
    args = parser.parse_args()
    return args

def list_databases_and_collections(client):
    total_documents = 0
    total_data_size = 0
    total_index_size = 0

    db_list = client.list_database_names()
    for db_name in db_list:
        db = client[db_name]
        print(f"Database: {db_name}")
        colls = db.list_collection_names()

        table = PrettyTable()
        table.field_names = ["Collection", "Documents", "Storage Size (bytes)", "Indexes", "Index Size (bytes)", "Total Data Size", "Total Index Size", "Avg Obj Size"]

        for coll_name in colls:
            coll = db[coll_name]
            coll_info = db.command("listCollections", filter={"name": coll_name})
            if coll_info["cursor"]["firstBatch"][0].get("type") == "view":
                print(f"  Collection: {coll_name} is a view, skipping stats")
                continue
            coll_stats = db.command("collStats", coll_name)
            document_count = coll_stats.get('count', 0)
            storage_size = coll_stats.get('size', 0)
            index_count = len(coll_stats.get('indexSizes', {}))
            index_size = coll_stats.get('totalIndexSize', 0)
            total_data_size_coll = coll_stats.get('storageSize', 0)
            avg_obj_size = coll_stats.get('avgObjSize', 0)

            total_documents += document_count
            total_data_size += total_data_size_coll
            total_index_size += index_size

            table.add_row([coll_name, document_count, storage_size, index_count, index_size, total_data_size_coll, index_size, avg_obj_size])

        print(table)

    print(f"Total Documents: {total_documents}")
    print(f"Total Data Size: {humanize.naturalsize(total_data_size, binary=True)}")
    print(f"Total Index Size: {humanize.naturalsize(total_index_size, binary=True)}")

    # Get server status for RAM usage
    server_status = client.admin.command("serverStatus")
    mem = server_status.get("mem", {})
    resident = mem.get("resident", 0)
    virtual = mem.get("virtual", 0)
    mapped = mem.get("mapped", 0)

    print(f"RAM Headroom: {humanize.naturalsize(virtual - resident, binary=True)}")
    print(f"RAM Used: {humanize.naturalsize(resident, binary=True)} ({(resident / virtual * 100):.1f}%)")

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

    # List collections for each shard
    list_databases_and_collections(client)

if __name__ == '__main__':
    main()
