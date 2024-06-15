import argparse
import logging
from pymongo import MongoClient, DESCENDING, ASCENDING
from datetime import datetime
import numpy as np

def setup_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')

def build_query(log_level):
    # Build the query based on log level
    base_query = {"op": {"$nin": ["getmore", "delete"]}}
    
    if log_level and log_level.lower() in ['panic', 'fatal', 'error']:
        base_query["err"] = {"$exists": True}
    elif log_level and log_level.lower() == 'warn':
        base_query["millis"] = {"$gte": 100}  
    elif log_level and log_level.lower() in ['info', 'debug']:
        # Include all logs
        pass
    elif log_level:
        raise ValueError(f"Invalid log level: {log_level}")

    return base_query

def run_mongo_query(db_name, username, password, auth_db, host, log_level, limit, order_by):
    
    if username and password:
        uri = f"mongodb://{username}:{password}@{host}/{auth_db}"
    else:
        uri = f"mongodb://{host}"
    
    logging.info(f"Connecting to MongoDB with URI: {uri}")
    
    
    client = MongoClient(uri)
    db = client[db_name]
    profile_collection = db.system.profile

    # Build query
    query = build_query(log_level)
    logging.debug(f"Query: {query}")
    
    # Sorting
    sort_order = []
    if order_by:
        for field in order_by.split(','):
            if field.startswith('-'):
                sort_order.append((field[1:], DESCENDING))
            else:
                sort_order.append((field, ASCENDING))
    
    logging.debug(f"Using sort order: {sort_order}")
    
    # Retrieve the profiling data
    if sort_order:
        cursor = profile_collection.find(query).sort(sort_order)
    else:
        cursor = profile_collection.find(query)
    
    if limit:
        cursor = cursor.limit(limit)
    
    profile_data = list(cursor)
    logging.info(f"Number of profile records found: {len(profile_data)}")

    if not profile_data:
        logging.warning("No data found")
        return

    
    exec_times = []
    docs_scanned = []
    docs_returned = []
    bytes_recv = []
    timestamps = []

    for entry in profile_data:
        exec_times.append(entry.get('millis', 0))
        docs_scanned.append(entry.get('docsExamined', 0))
        docs_returned.append(entry.get('nreturned', 0))
        bytes_recv.append(entry.get('responseLength', 0))
        timestamps.append(entry.get('ts'))

    
    total_docs = len(profile_data)
    total_exec_time = sum(exec_times)
    total_docs_scanned = sum(docs_scanned)
    total_docs_returned = sum(docs_returned)
    total_bytes_recv = sum(bytes_recv)
    avg_exec_time = np.mean(exec_times)
    avg_docs_scanned = np.mean(docs_scanned)
    avg_docs_returned = np.mean(docs_returned)
    avg_bytes_recv = np.mean(bytes_recv)
    stddev_exec_time = np.std(exec_times)
    stddev_docs_scanned = np.std(docs_scanned)
    stddev_docs_returned = np.std(docs_returned)
    stddev_bytes_recv = np.std(bytes_recv)

    # Print detailed statistics for each query
    for i, entry in enumerate(profile_data):
        query_id = entry.get('opid', 'N/A')
        if query_id == 'N/A':
            command = entry.get('command', {})
            if 'lsid' in command and 'id' in command['lsid']:
                query_id = command['lsid']['id'].hex()
            elif 'txnNumber' in command:
                query_id = str(command['txnNumber'])
            elif 'queryHash' in command:
                query_id = str(command['queryHash'])
        
        start_time = entry.get('ts', 'N/A')
        if isinstance(start_time, datetime):
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        else:
            start_time_str = 'N/A'

        exec_time = entry.get('millis', 0)
        docs_examined = entry.get('docsExamined', 0)
        docs_returned = entry.get('nreturned', 0)
        response_length = entry.get('responseLength', 0)
        ns = entry.get('ns', 'N/A')
        query = entry.get('query', entry.get('command', 'N/A'))

        print(f"# Query {i+1}:  0.00 QPS, ID {query_id}")
        print(f"# Ratio    1.00  (docs scanned/returned)")
        print(f"# Time range: {start_time_str} to {start_time_str}")
        print("# Attribute            pct     total        min         max        avg         95%        stddev      median")
        print("# ==================   ===   ========    ========    ========    ========    ========     =======    ========")
        print(f"# Exec Time ms         0         0           0           {exec_time:.2f}           {avg_exec_time:.2f}           0           {stddev_exec_time:.2f}           0")
        print(f"# Docs Scanned         0    {total_docs_scanned:.2f}        0.00       {docs_examined:.2f}        {avg_docs_scanned:.2f}       0           {stddev_docs_scanned:.2f}        0.00")
        print(f"# Docs Returned        0    {total_docs_returned:.2f}        0.00       {docs_returned:.2f}        {avg_docs_returned:.2f}       0           {stddev_docs_returned:.2f}        0.00")
        print(f"# Bytes recv           0    {total_bytes_recv:.2f}        0.00       {response_length:.2f}        {avg_bytes_recv:.2f}       0           {stddev_bytes_recv:.2f}        0.00")
        print("# String:")
        print(f"# Namespaces          {ns}")
        print(f"# Fingerprint         {query}\n")

def main():
    parser = argparse.ArgumentParser(description="MongoDB Profiling Query Script")
    parser.add_argument('-u', '--username', help="Specifies the user name for connecting to a server with authentication enabled.")
    parser.add_argument('-p', '--password', help="Specifies the password to use when connecting to a server with authentication enabled.")
    parser.add_argument('-a', '--auth_db', help="Specifies the database used to establish credentials and privileges with a MongoDB server.", default='admin')
    parser.add_argument('-d', '--database', required=True, help="Specifies which database to profile")
    parser.add_argument('--mongo_host', help="Specifies the MongoDB host", default='localhost:27017')
    parser.add_argument('-l', '--log_level', help="Specifies the log level: panic, fatal, error, warn, info, debug", default=None)
    parser.add_argument('-n', '--limit', type=int, help="Limits the number of queries to show. Default : everything", default=0)
    parser.add_argument('-o', '--order_by', help="Specifies the sorting order using fields: count, ratio, query-time, docs-scanned, docs-returned", default='')

    args = parser.parse_args()

    setup_logging(args.log_level or 'debug')  # Default to 'debug' if log_level is not provided

    run_mongo_query(args.database, args.username, args.password, args.auth_db, args.mongo_host, args.log_level, args.limit, args.order_by)

if __name__ == "__main__":
    main()
