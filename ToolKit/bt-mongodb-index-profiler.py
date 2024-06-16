import argparse
from pymongo import MongoClient

def get_all_databases(client):
    return [db for db in client.list_database_names() if db not in ('admin', 'local', 'config')]

def get_all_collections(db):
    return db.list_collection_names()

def fetch_indexes(collection):
    return collection.index_information()

def is_prefix(index1, index2):
    keys1 = index1
    keys2 = index2
    if len(keys1) >= len(keys2):
        return False
    for i in range(len(keys1)):
        if keys1[i] != keys2[i]:
            return False
    return True

def check_duplicated_indexes(db, collection):
    indexes = fetch_indexes(collection)
    to_drop = set()
    index_names = list(indexes.keys())

    for i in range(len(index_names)):
        for j in range(i + 1, len(index_names)):
            idx1 = indexes[index_names[i]]['key']
            idx2 = indexes[index_names[j]]['key']
            if is_prefix(idx1, idx2):
                to_drop.add(index_names[i])
            elif is_prefix(idx2, idx1):
                to_drop.add(index_names[j])

    return list(to_drop)

def check_unused_indexes(db, collection):
    try:
        index_stats = collection.aggregate([{"$indexStats": {}}])
        unused_indexes = []
        for index in index_stats:
            if index.get('accesses', {}).get('ops', 0) == 0:
                unused_indexes.append(index['name'])
        return unused_indexes
    except Exception as e:
        print(f"Error checking unused indexes: {e}")
        return []

def main(args):
    client = MongoClient(
        host=args.host,
        port=args.port,
        username=args.user,
        password=args.password
    )

    databases = []

    if args.all_databases:
        databases = get_all_databases(client)
    elif args.databases:
        databases = args.databases.split(',')
    else:
        print("No databases specified. Use --all-databases or --databases to specify databases.")
        return

    result_count = 1

    for db_name in databases:
        db = client[db_name]
        collections = []

        if args.all_collections:
            collections = get_all_collections(db)
        elif args.collections:
            collections = args.collections.split(',')
        else:
            print(f"No collections specified for database '{db_name}'. Use --all-collections or --collections to specify collections.")
            continue

        for col_name in collections:
            collection = db[col_name]

            if args.check_duplicated or args.check_all:
                duplicates = check_duplicated_indexes(db, collection)
                if duplicates:
                    print(f"{result_count}- In database '{db_name}', collection '{col_name}', drop indexes: {duplicates}")
                    result_count += 1

            if args.check_unused or args.check_all:
                unused = check_unused_indexes(db, collection)
                if unused:
                    print(f"{result_count}- In database '{db_name}', collection '{col_name}', unused indexes: {unused}")
                    result_count += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check for duplicated and unused indexes in MongoDB.')
    parser.add_argument('--check-duplicated', action='store_true', help='Run checks for duplicated indexes.')
    parser.add_argument('--check-unused', action='store_true', help='Run checks for unused indexes.')
    parser.add_argument('--check-all', action='store_true', help='Run all checks both unused and duplicated.')
    parser.add_argument('--all-databases', action='store_true', help='Check in all databases excluding system dbs.')
    parser.add_argument('--databases', type=str, help='Comma separated list of databases to check.')
    parser.add_argument('--all-collections', action='store_true', help='Check in all collections in the selected databases.')
    parser.add_argument('--collections', type=str, help='Comma separated list of collections to check.')

    # Add MongoDB connection arguments
    parser.add_argument('--host', type=str, default='localhost', help='MongoDB host')
    parser.add_argument('--port', type=int, default=27017, help='MongoDB port')
    parser.add_argument('--user', type=str, help='MongoDB username')
    parser.add_argument('--password', type=str, help='MongoDB password')

    args = parser.parse_args()

    if args.check_duplicated or args.check_unused or args.check_all:
        main(args)
    else:
        print("Please provide either --check-duplicated, --check-unused, or --check-all argument to run the script.")
