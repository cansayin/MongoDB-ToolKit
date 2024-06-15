import pymongo
import pprint
import argparse

def get_command_line_args():
    parser = argparse.ArgumentParser(description='Get index statistics from a MongoDB collection or all collections.')
    parser.add_argument('--database', type=str, help='The name of the database.')
    parser.add_argument('--collection', type=str, help='The name of the collection.')
    parser.add_argument('--host', type=str, default='localhost', help='The host of the MongoDB server. Default is localhost.')
    parser.add_argument('--port', type=int, default=27017, help='The port of the MongoDB server. Default is 27017.')
    parser.add_argument('--user', type=str, help='The username for MongoDB authentication.')
    parser.add_argument('--password', type=str, help='The password for MongoDB authentication.')
    parser.add_argument('--show-all', action='store_true', help='If specified, run the command for all collections in the cluster.')
    parser.add_argument('--ignore-databases', type=str, nargs='*', help='List of databases to ignore when --show-all is used.')

    return parser.parse_args()

def run_index_stats(collection):
    result_count = 0
    try:
        result = collection.aggregate([{ '$indexStats': { } }])
        for doc in result:
            pprint.pprint(doc)
            print(" ")  # Add #### at the end of each result
            result_count += 1
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred: {e}")
    return result_count

def main():
    # Get command-line arguments
    args = get_command_line_args()

    # Create the MongoDB connection string
    if args.user and args.password:
        connection_string = f"mongodb://{args.user}:{args.password}@{args.host}:{args.port}/"
    else:
        connection_string = f"mongodb://{args.host}:{args.port}/"

    # Establish a connection to MongoDB
    client = pymongo.MongoClient(connection_string)

    total_results = 0

    if args.show_all:
        # Iterate over all databases and collections, ignoring specified databases
        ignore_dbs = args.ignore_databases if args.ignore_databases else []
        for db_name in client.list_database_names():
            if db_name in ignore_dbs:
                print(f"Ignoring database {db_name}")
                continue
            db = client[db_name]
            for coll_name in db.list_collection_names():
                print(f"#### Running index stats for {db_name}.{coll_name} ####")
                collection = db[coll_name]
                total_results += run_index_stats(collection)
    else:
        if not args.database or not args.collection:
            print("You must specify both --database and --collection unless --show-all is used.")
            return
        
        db = client[args.database]
        collection = db[args.collection]
        print(f"Running index stats for {args.database}.{args.collection} ####")
        total_results += run_index_stats(collection)

    # Close the MongoDB connection
    client.close()

    print(f"Total number of results returned: {total_results} ####")

if __name__ == "__main__":
    main()
