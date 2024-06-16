import argparse
from pymongo import MongoClient
from pymongo.errors import OperationFailure

def get_resource_intensive_operations(client, check_mem, check_cpu, ignore_dbs, order_by, limit):
    admin_db = client.admin
    try:
        current_op = admin_db.command('currentOp')
    except OperationFailure as e:
        print(f"Failed to run currentOp command: {e}")
        return []

    ops = current_op.get('inprog', [])
    
    if ignore_dbs:
        ops = [op for op in ops if op.get('ns', '').split('.')[0] not in ignore_dbs]

    if check_mem and check_cpu:
        ops.sort(key=lambda x: (x.get('cpu_usage', 0), x.get('mem_usage', 0)), reverse=True)
    elif check_mem:
        ops.sort(key=lambda x: x.get('mem_usage', 0), reverse=True)
    elif check_cpu:
        ops.sort(key=lambda x: x.get('cpu_usage', 0), reverse=True)

    ops.sort(key=lambda x: x.get('secs_running', 0), reverse=(order_by == 'desc'))

    if limit:
        ops = ops[:limit]

    return ops

def main():
    parser = argparse.ArgumentParser(description='Check MongoDB running operations consuming most CPU and RAM.')
    parser.add_argument('--host', default='localhost', help='MongoDB host (default: localhost)')
    parser.add_argument('--port', type=int, default=27017, help='MongoDB port (default: 27017)')
    parser.add_argument('--user', default=None, help='MongoDB user (default: None)')
    parser.add_argument('--password', default=None, help='MongoDB password (default: None)')
    parser.add_argument('--check', choices=['mem', 'cpu'], help='Check memory or CPU usage')
    parser.add_argument('--check-both', action='store_true', help='Check both memory and CPU usage')
    parser.add_argument('--order-by', choices=['asc', 'desc'], default='desc', help='Order results by ascending or descending secs_running (default: descending)')
    parser.add_argument('--limit', type=int, help='Limit the number of results')
    parser.add_argument('--all-databases', action='store_true', help='Include operations from all databases')
    parser.add_argument('--ignore-databases', nargs='*', default=[], help='Databases to ignore when using --all-databases')

    args = parser.parse_args()

    if not args.check and not args.check_both:
        print("You must specify either --check or --check-both.")
        return

    client = MongoClient(host=args.host, port=args.port, username=args.user, password=args.password, authSource='admin')

    if args.all_databases:
        ignore_dbs = args.ignore_databases
    else:
        ignore_dbs = []

    check_mem = args.check in ['mem'] or args.check_both
    check_cpu = args.check in ['cpu'] or args.check_both

    intensive_ops = get_resource_intensive_operations(client, check_mem, check_cpu, ignore_dbs, args.order_by, args.limit)

    for op in intensive_ops:
        print(op)

if __name__ == '__main__':
    main()
