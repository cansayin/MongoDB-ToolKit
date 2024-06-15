from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import argparse
import getpass
import socket
import datetime

def get_mongo_client(host, port, username, password, authdb):
    if username and password:
        uri = f"mongodb://{username}:{password}@{host}:{port}/{authdb}"
    else:
        uri = f"mongodb://{host}:{port}/"
    return MongoClient(uri)

def get_shard_info(client):
    shards = client.admin.command('listShards')['shards']
    return shards

def get_repl_set_member_info(repl_client, repl_set_name):
    try:
        repl_status = repl_client.admin.command('replSetGetStatus')
        members_info = []
        for member in repl_status['members']:
            members_info.append({
                'ID': member['_id'],
                'Host': member['name'],
                'Type': member['stateStr'],
                'ReplSet': repl_set_name
            })
        return members_info
    except Exception as e:
        print(f"Error retrieving replica set member info: {e}")
        return []

def get_instances_info(client):
    try:
        shards = get_shard_info(client)
        instances = []
        processed_repl_sets = set()
        for shard in shards:
            repl_set_name, hosts = shard['host'].split('/', 1)
            if repl_set_name in processed_repl_sets:
                continue
            processed_repl_sets.add(repl_set_name)
            primary_host = hosts.split(',')[0]  # Use the first host to get replica set status
            repl_client = MongoClient(primary_host)
            instance_info = get_repl_set_member_info(repl_client, repl_set_name)
            if instance_info:
                instances.extend(instance_info)
        return instances
    except Exception as e:
        print(f"Error retrieving cluster info: {e}")
        return []

def get_security_info(client):
    try:
        users_info = client['admin'].command('usersInfo')
        roles_info = client['admin'].command('rolesInfo')

        auth_status = "enabled" if client.server_info().get('setParameter', {}).get('authenticationMechanisms', []) else "disabled"
        ssl_status = "enabled" if 'ssl' in client.server_info() else "disabled"

        return {
            "Users": len(users_info['users']),
            "Roles": len(roles_info['roles']),
            "Auth": auth_status,
            "SSL": ssl_status
        }
    except Exception as e:
        print(f"Error retrieving security info: {e}")
        return {
            "Users": 0,
            "Roles": 0,
            "Auth": "disabled",
            "SSL": "disabled"
        }

def get_oplog_info(client):
    try:
        shards = get_shard_info(client)
        oplog_size_mb = 0
        oplog_used_mb = 0
        oplog_length_hours = 0
        last_election_date = None

        for shard in shards:
            repl_set_name, hosts = shard['host'].split('/', 1)
            primary_host = hosts.split(',')[0]
            repl_client = MongoClient(primary_host)
            oplog = repl_client.local['oplog.rs']
            oplog_stats = repl_client.admin.command('collStats', 'oplog.rs')
            oplog_start = oplog.find().sort('$natural', 1).limit(1).next()
            oplog_end = oplog.find().sort('$natural', -1).limit(1).next()

            oplog_size_mb += oplog_stats['storageSize'] / (1024 * 1024)
            oplog_used_mb += oplog_stats['size'] / (1024 * 1024)
            oplog_length_hours += (oplog_end['ts'].as_datetime() - oplog_start['ts'].as_datetime()).total_seconds() / 3600
            if not last_election_date:
                last_election_date = repl_client.admin.command('replSetGetStatus')['members'][0]['electionDate']

        return {
            "Oplog Size": f"{oplog_size_mb:.2f} Mb",
            "Oplog Used": f"{oplog_used_mb:.2f} Mb",
            "Oplog Length": f"{oplog_length_hours:.2f} hours",
            "Last Election": last_election_date.strftime("%Y-%m-%d %H:%M:%S %Z") if last_election_date else "N/A"
        }
    except Exception as e:
        print(f"Error retrieving oplog info: {e}")
        return {
            "Oplog Size": "N/A",
            "Oplog Used": "N/A",
            "Oplog Length": "N/A",
            "Last Election": "N/A"
        }

def get_cluster_info(client):
    try:
        db_names = client.list_database_names()
        total_collections = 0
        sharded_collections = 0
        unsharded_collections = 0
        sharded_data_size = 0
        unsharded_data_size = 0

        for db_name in db_names:
            db = client[db_name]
            collection_names = db.list_collection_names()
            total_collections += len(collection_names)
            for coll_name in collection_names:
                coll_stats = db.command("collStats", coll_name)
                if "sharded" in coll_stats:
                    sharded_collections += 1
                    sharded_data_size += coll_stats["size"]
                else:
                    unsharded_collections += 1
                    unsharded_data_size += coll_stats["size"]

        return {
            "Databases": len(db_names),
            "Collections": total_collections,
            "Sharded Collections": sharded_collections,
            "Unsharded Collections": unsharded_collections,
            "Sharded Data Size": f"{sharded_data_size / (1024 * 1024 * 1024):.2f} GB",
            "Unsharded Data Size": f"{unsharded_data_size / 1024:.2f} KB"
        }
    except Exception as e:
        print(f"Error retrieving cluster info: {e}")
        return {
            "Databases": "N/A",
            "Collections": "N/A",
            "Sharded Collections": "N/A",
            "Unsharded Collections": "N/A",
            "Sharded Data Size": "N/A",
            "Unsharded Data Size": "N/A"
        }

def print_instances(instances):
    print("# Instances ####################################################################################")
    print(f"{'ID':<4} {'Host':<30} {'Type':<35} {'ReplSet'}")
    for instance in instances:
        print(f"{instance['ID']:<4} {instance['Host']:<30} {instance['Type']:<35} {instance['ReplSet']}")
    print()

def print_report(client):
    server_status = client.admin.command('serverStatus')
    build_info = client.admin.command('buildInfo')
    
    report = {
        "User": getpass.getuser(),
        "PID Owner": server_status['pid'],
        "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "Hostname": socket.gethostname(),
        "Version": build_info['version'],
        "Built On": build_info['bits'],
        "Started": datetime.datetime.fromtimestamp(server_status['uptimeMillis'] / 1000).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "Datadir": server_status['storageEngine']['dbPath'] if 'storageEngine' in server_status else 'N/A',
        "Process Type": server_status['process']
    }
    
    print("# Report On 0 ########################################")
    for key, value in report.items():
        print(f"{key:>25} | {value}")
    print()

def print_running_ops(client):
    ops_info = client.admin.command('serverStatus')['opcounters']
    ops_stats = {
        "Insert": ops_info.get('insert', 0),
        "Query": ops_info.get('query', 0),
        "Update": ops_info.get('update', 0),
        "Delete": ops_info.get('delete', 0),
        "GetMore": ops_info.get('getmore', 0),
        "Command": ops_info.get('command', 0)
    }
    
    print("# Running Ops ##################################################################################")
    print(f"{'Type':<13} {'Min':<10} {'Max':<10} {'Avg':<10}")
    for op, count in ops_stats.items():
        print(f"{op:<13} {0:<10} {count:<10} {count//5:<10}/5s")
    print()

def print_security_info(security_info):
    print("# Security #####################################################################################")
    print(f"{'Users':<13} {security_info['Users']}")
    print(f"{'Roles':<13} {security_info['Roles']}")
    print(f"{'Auth':<13} {security_info['Auth']}")
    print(f"{'SSL':<13} {security_info['SSL']}")
    print()

def print_oplog_info(oplog_info):
    print("# Oplog ########################################################################################")
    for key, value in oplog_info.items():
        print(f"{key:<15} {value}")
    print()

def print_cluster_info(cluster_info):
    print("# Cluster wide #################################################################################")
    for key, value in cluster_info.items():
        print(f"{key:<25} {value}")
    print()

def main():
    parser = argparse.ArgumentParser(description="MongoDB Sharded Cluster Info Retriever")
    parser.add_argument("--host", default="localhost", help="MongoDB host")
    parser.add_argument("--port", type=int, default=27017, help="MongoDB port")
    parser.add_argument("--username", help="MongoDB username")
    parser.add_argument("--password", help="MongoDB password")
    parser.add_argument("--authdb", default="admin", help="MongoDB authentication database")

    args = parser.parse_args()

    client = get_mongo_client(args.host, args.port, args.username, args.password, args.authdb)
    
    try:
        # Check the connection
        client.admin.command('ping')
        print("######## BlancoByte ToolKit - MongoDB Sharded Summary Tool ########")
        print("Connected to MongoDB successfully!")
    except ConnectionFailure:
        print("Failed to connect to MongoDB")
        return

    instances = get_instances_info(client)
    print_instances(instances)
    print_report(client)
    print_running_ops(client)
    security_info = get_security_info(client)
    print_security_info(security_info)
    oplog_info = get_oplog_info(client)
    print_oplog_info(oplog_info)
    cluster_info = get_cluster_info(client)
    print_cluster_info(cluster_info)

if __name__ == "__main__":
    main()
