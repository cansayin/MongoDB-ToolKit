import argparse
from pymongo import MongoClient
from pymongo.errors import OperationFailure

def get_long_running_operations(client, threshold_seconds, ignore_dbs):
    admin_db = client.admin
    try:
        current_op = admin_db.command('currentOp')
    except OperationFailure as e:
        print(f"Failed to run currentOp command: {e}")
        return []

    long_running_ops = [
        op for op in current_op.get('inprog', [])
        if op.get('secs_running', 0) >= threshold_seconds and op.get('ns', '').split('.')[0] not in ignore_dbs
    ]
    return long_running_ops

def kill_operation(client, op_id):
    try:
        client.admin.command('killOp', op=op_id)
        print(f"Killed operation {op_id}")
    except OperationFailure as e:
        print(f"Failed to kill operation {op_id}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Manage long-running MongoDB queries.')
    parser.add_argument('--host', default='localhost', help='MongoDB host (default: localhost)')
    parser.add_argument('--port', type=int, default=27017, help='MongoDB port (default: 27017)')
    parser.add_argument('--user', default=None, help='MongoDB user (default: None)')
    parser.add_argument('--password', default=None, help='MongoDB password (default: None)')
    parser.add_argument('--busy-time', type=int, required=True, help='Threshold for long-running queries in seconds')
    parser.add_argument('--action', choices=['kill', 'print'], required=True, help='Action to perform on long-running queries')
    parser.add_argument('--all-databases', action='store_true', help='Include operations from all databases')
    parser.add_argument('--ignore-databases', nargs='*', default=[], help='Databases to ignore when using --all-databases')

    args = parser.parse_args()

    client = MongoClient(host=args.host, port=args.port, username=args.user, password=args.password, authSource='admin')

    if args.all_databases:
        long_running_ops = get_long_running_operations(client, args.busy_time, args.ignore_databases)
    else:
        long_running_ops = get_long_running_operations(client, args.busy_time, [])

    if args.action == 'print':
        for op in long_running_ops:
            print(op)
    elif args.action == 'kill':
        for op in long_running_ops:
            kill_operation(client, op['opid'])

if __name__ == '__main__':
    main()
