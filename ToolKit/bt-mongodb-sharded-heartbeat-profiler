import pymongo
from pymongo import MongoClient
import argparse
import time

def get_replica_set_status(host, port, username, password):
    if username and password:
        uri = f"mongodb://{username}:{password}@{host}:{port}/admin"
    else:
        uri = f"mongodb://{host}:{port}/admin"
        
    client = MongoClient(uri)
    
    try:
        status = client.admin.command('replSetGetStatus')
        return status
    except Exception as e:
        print(f"Error getting replSetGetStatus: {e}")
        return None
    finally:
        client.close()

def check_shard_heartbeat(shard_uri, username, password):
    client = MongoClient(shard_uri)
    shard_status = client.admin.command('listShards')
    
    heartbeat_info = {}
    
    for shard in shard_status['shards']:
        shard_conn_str = shard['host']
        primary_host = shard_conn_str.split('/')[1].split(',')[0]  # Get primary host
        print(f"Checking heartbeat for shard: {shard['_id']} at {primary_host}")
        
        host, port = primary_host.split(':')
        repl_status = get_replica_set_status(host, port, username, password)
        
        if repl_status:
            for member in repl_status['members']:
                heartbeat_info[member['name']] = {
                    'state': member['stateStr'],
                    'health': member['health'],
                    'uptime': member['uptime'],
                    'lastHeartbeat': member.get('lastHeartbeat', 'N/A'),
                    'lastHeartbeatRecv': member.get('lastHeartbeatRecv', 'N/A'),
                    'lastHeartbeatMessage': member.get('lastHeartbeatMessage', 'N/A')
                }
    
    return heartbeat_info

def analyze_heartbeat_info(heartbeat_info):
    current_time = time.time()
    issues = []
    
    for member, info in heartbeat_info.items():
        last_heartbeat = info.get('lastHeartbeat', 'N/A')
        last_heartbeat_recv = info.get('lastHeartbeatRecv', 'N/A')
        last_heartbeat_message = info.get('lastHeartbeatMessage', 'N/A')
        
        if last_heartbeat != 'N/A' and last_heartbeat_recv != 'N/A':
            time_since_last_heartbeat = current_time - last_heartbeat_recv.timestamp()
            
            if time_since_last_heartbeat > 10:
                issues.append(f"Member {member} has not received a heartbeat in over 10 seconds.")
                
        if last_heartbeat_message and last_heartbeat_message != 'N/A':
            issues.append(f"Member {member} reports a heartbeat issue: {last_heartbeat_message}")
    
    return issues

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check heartbeat status in a MongoDB sharded cluster.')
    parser.add_argument('--host', type=str, default='localhost', help='MongoDB host (default: localhost)')
    parser.add_argument('--port', type=str, default='27017', help='MongoDB port (default: 27017)')
    parser.add_argument('--username', type=str, help='MongoDB username')
    parser.add_argument('--password', type=str, help='MongoDB password')

    args = parser.parse_args()
    
    if args.username and args.password:
        shard_uri = f"mongodb://{args.username}:{args.password}@{args.host}:{args.port}/admin"
    else:
        shard_uri = f"mongodb://{args.host}:{args.port}/admin"
    
    heartbeat_info = check_shard_heartbeat(shard_uri, args.username, args.password)
    
    if heartbeat_info:
        print("Replication heartbeat information:")
        for member, info in heartbeat_info.items():
            print(f"\nMember: {member}")
            for key, value in info.items():
                print(f"  {key}: {value}")
        
        issues = analyze_heartbeat_info(heartbeat_info)
        
        if issues:
            print("\nIssues found with heartbeat:")
            for issue in issues:
                print(f"- {issue}")
                
            print("\nSuggestions:")
            print("- Ensure network stability between nodes.")
            print("- Check MongoDB logs for more detailed error messages.")
            print("- Verify that the MongoDB configuration is correct.")
        else:
            print("\nNo issues found with heartbeat.")
