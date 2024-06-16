# MongoDB-ToolKit
MongoDB ToolKit for Monitoring &amp; Troubleshooting

Welcome to the MongoDB ToolKit, a comprehensive suite of Python scripts designed to help you monitor and troubleshoot your MongoDB clusters effectively. This toolkit includes various scripts tailored for different aspects of MongoDB management, from sharded and replicated cluster summaries to index profiling, heartbeat monitoring and more.

Required Packages
- Some scripts may require; humanize, psutil or prettytable.
- If you encounter an error due to missing packages, please install them.
- Example: pip install prettytable

## bt-mongodb-sharded-summary & bt-mongodb-replicated-summary

This script connects to a MongoDB replica set and retrieves detailed information about the cluster. It provides insights into the replica set members, security settings, oplog details, and cluster-wide statistics.

Features:

- Replica Set Information: Lists all the members of the replica set along with their roles (primary, secondary, etc.).
- Cluster Report: Displays the user, PID owner, time, hostname, MongoDB version, and process type.
- Running Operations: Provides statistics on the types of operations being performed (insert, query, update, delete, getmore, command).
- Security Details: Shows the number of users and roles, and whether authentication and SSL are enabled.
- Oplog Information: Details the size, used space, length, and the time of the last election.
- Cluster-wide Statistics: Summarizes the number of databases, collections (sharded and unsharded), and the data sizes for both sharded and unsharded collections.

### Usage
```
python3 bt-mongodb-sharded-summary --help

usage: bt-mongodb-sharded-summary [-h] [--host HOST] [--port PORT] [--username USERNAME] [--password PASSWORD] [--authdb AUTHDB]

MongoDB Sharded Cluster Info Retriever

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          MongoDB host
  --port PORT          MongoDB port
  --username USERNAME  MongoDB username
  --password PASSWORD  MongoDB password
  --authdb AUTHDB      MongoDB authentication database
```
#### Example
```
python3 bt-mongodb-sharded-summary       

Connected to MongoDB successfully!
# Instances ####################################################################################
ID   Host                           Type                                ReplSet
0    shard01-a:27017                PRIMARY                             rs-shard-01
1    shard01-b:27017                SECONDARY                           rs-shard-01
2    shard01-c:27017                SECONDARY                           rs-shard-01
0    shard02-a:27017                SECONDARY                           rs-shard-02
1    shard02-b:27017                PRIMARY                             rs-shard-02
2    shard02-c:27017                SECONDARY                           rs-shard-02
0    shard03-a:27017                PRIMARY                             rs-shard-03
1    shard03-b:27017                SECONDARY                           rs-shard-03
2    shard03-c:27017                SECONDARY                           rs-shard-03

# Report On 0 ########################################
                     User | root
                PID Owner | 1
                     Time | 2024-06-15 21:06:45 
                 Hostname | f87ace4a3ab1
                  Version | 6.0.1
                 Built On | 64
                  Started | 1970-01-01 02:43:07 
                  Datadir | N/A
             Process Type | mongos

# Running Ops ##################################################################################
Type          Min        Max        Avg       
Insert        0          0          0         /5s
Query         0          8          1         /5s
Update        0          0          0         /5s
Delete        0          0          0         /5s
GetMore       0          0          0         /5s
Command       0          968        193       /5s

# Security #####################################################################################
Users         0
Roles         0
Auth          disabled
SSL           disabled

# Oplog ########################################################################################
Oplog Size      0.00 Mb
Oplog Used      0.00 Mb
Oplog Length    223.68 hours
Last Election   2024-06-15 18:24:00 

# Cluster wide #################################################################################
Databases                 4
Collections               23
Sharded Collections       23
Unsharded Collections     0
Sharded Data Size         0.00 GB
Unsharded Data Size       0.00 KB

```

## bt-mongodb-index-profiler

This Python script connects to a MongoDB instance and checks for duplicated and unused indexes across specified databases and collections. It helps in optimizing MongoDB performance by identifying and suggesting the removal of unnecessary indexes.

Features:

- Check Duplicated Indexes: Identifies indexes that are prefixes of other indexes in the same collection.
- Check Unused Indexes: Detects indexes that have not been used, indicating they may be unnecessary.
- Combined Check: Runs both checks (duplicated and unused) in one execution.


### Usage
```
python3 bt-mongodb-index-profiler --help

usage: bt-mongodb-index-profiler [-h] [--check-duplicated] [--check-unused] [--check-all] [--all-databases] [--databases DATABASES] [--all-collections] [--collections COLLECTIONS]
                                 [--host HOST] [--port PORT] [--user USER] [--password PASSWORD]

Check for duplicated and unused indexes in MongoDB.

optional arguments:
  -h, --help            show this help message and exit
  --check-duplicated    Run checks for duplicated indexes.
  --check-unused        Run checks for unused indexes.
  --check-all           Run all checks both unused and duplicated.
  --all-databases       Check in all databases excluding system dbs.
  --databases DATABASES
                        Comma separated list of databases to check.
  --all-collections     Check in all collections in the selected databases.
  --collections COLLECTIONS
                        Comma separated list of collections to check.
  --host HOST           MongoDB host
  --port PORT           MongoDB port
  --user USER           MongoDB username
  --password PASSWORD   MongoDB password
```
#### Example
```
python3 bt-mongodb-index-profiler --check-all --all-databases --all-collections

1- In database 'MyDatabase', collection 'MyCollection', unused indexes: ['_id_', 'oemNumber_hashed_zipCode_1_supplierId_1', 'idx_01', 'idx_02', '_id_', 'oemNumber_hashed_zipCode_1_supplierId_1', '_id_', 'oemNumber_hashed_zipCode_1_supplierId_1']. You can delete these.
2- In database 'MyDatabase', collection 'products', unused indexes: ['_id_']. You can delete these.
3- In database 'testdb', collection 'test_col', index 'idx_02' is a duplicate of 'idx_01'. You can delete 'idx_02'.
4- In database 'testdb', collection 'test_col', unused indexes: ['_id_', 'idx_02', 'idx_01']. You can delete these.
```


## bt-mongodb-index-usage

This Python script retrieves index statistics from a MongoDB collection or all collections in a MongoDB cluster. It connects to a MongoDB instance and runs the index statistics aggregation command on the specified collection(s), and prints the results to the console.

Features:
- Connect to a MongoDB instance using optional authentication.
- Retrieve index statistics for a specified database and collection.
- Retrieve index statistics for all collections in all databases, with the option to ignore specified databases.

### Usage
```
python3 bt-mongodb-index-usage --help

usage: bt-mongodb-index-usage [-h] [--database DATABASE] [--collection COLLECTION] [--host HOST] [--port PORT] [--user USER] [--password PASSWORD] [--show-all]
                              [--ignore-databases [IGNORE_DATABASES [IGNORE_DATABASES ...]]]

Get index statistics from a MongoDB collection or all collections.

optional arguments:
  -h, --help            show this help message and exit
  --database DATABASE   The name of the database.
  --collection COLLECTION
                        The name of the collection.
  --host HOST           The host of the MongoDB server. Default is localhost.
  --port PORT           The port of the MongoDB server. Default is 27017.
  --user USER           The username for MongoDB authentication.
  --password PASSWORD   The password for MongoDB authentication.
  --show-all            If specified, run the command for all collections in the cluster.
  --ignore-databases [IGNORE_DATABASES [IGNORE_DATABASES ...]]
                        List of databases to ignore when --show-all is used.

```
#### Example
```
python3 bt-mongodb-index-usage --database testdb --collection test_col

name: _id_
key: {'_id': 1}
host: 4ef314225763:27017
ops: 0
since: 2024-06-16 14:25:56.935000
shard: rs-shard-01
spec: {'v': 2, 'key': {'_id': 1}, 'name': '_id_'}

name: oemNumber_hashed_zipCode_1_supplierId_1
key: {'oemNumber': 'hashed', 'zipCode': 1, 'supplierId': 1}
host: 4ef314225763:27017
ops: 0
since: 2024-06-16 14:25:56.935000
shard: rs-shard-01
spec: {'v': 2, 'key': {'oemNumber': 'hashed', 'zipCode': 1, 'supplierId': 1}, 'name': 'oemNumber_hashed_zipCode_1_supplierId_1'}

name: idx_01
key: {'f1': 1, 'f2': -1, 'f3': 1, 'f4': 1}
host: 4ef314225763:27017
ops: 0
since: 2024-06-16 14:25:56.935000
shard: rs-shard-01
spec: {'v': 2, 'key': {'f1': 1, 'f2': -1, 'f3': 1, 'f4': 1}, 'name': 'idx_01'}

Total number of results returned: 42

```


## bt-mongodb-kill-processes

This Python script helps manage long-running queries in a MongoDB cluster. You can either print or kill queries that have been running longer than a specified threshold time.


Features:

- Print or Kill Long-Running Queries:** Specify a threshold time in seconds to identify long-running queries and either print or kill them.
- Cluster-Wide Operation:** Option to operate on all databases in the cluster.
- Ignore Specific Databases:** Option to exclude specific databases from the operation.
- Default MongoDB Connection Parameters:** Defaults to `localhost:27017` if no host or port is specified.

### Usage
```
python3 bt-mongodb-kill-processes --help

usage: bt-mongodb-kill-processes [-h] [--host HOST] [--port PORT] [--user USER] [--password PASSWORD] --busy-time BUSY_TIME --action {kill,print} [--all-databases]
                                 [--ignore-databases [IGNORE_DATABASES [IGNORE_DATABASES ...]]]

Manage long-running MongoDB queries.

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           MongoDB host (default: localhost)
  --port PORT           MongoDB port (default: 27017)
  --user USER           MongoDB user (default: None)
  --password PASSWORD   MongoDB password (default: None)
  --busy-time BUSY_TIME
                        Threshold for long-running queries in seconds
  --action {kill,print}
                        Action to perform on long-running queries
  --all-databases       Include operations from all databases
  --ignore-databases [IGNORE_DATABASES [IGNORE_DATABASES ...]]
                        Databases to ignore when using --all-databases


```
#### Example
```
python3 bt-mongodb-kill-processes --busy-time 2 --action kill --all-databases
Killed operation rs-shard-01:172867
Killed operation rs-shard-01:172946
Killed operation rs-shard-01:172861
Killed operation rs-shard-01:172863
Killed operation rs-shard-01:172945
Killed operation rs-shard-01:172864
...
...

Total number of killed operations: 6

```
```
python3 bt-mongodb-kill-processes --busy-time 2 --action print --all-databases --ignore-databases admin,config,testdb

{'shard': 'rs-shard-03', 'type': 'op', 'host': '96125cbd04b9:27017', 'desc': 'conn39', 'connectionId': 39, 'client_s': '172.18.0.2:56968', 'clientMetadata': {'driver': {'name': 'NetworkInterfaceTL-ReplicaSetMonitor-TaskExecutor', 'version': '6.0.1'}, 'os': {'type': 'Linux', 'name': 'Ubuntu', 'architecture': 'aarch64', 'version': '20.04'}}, 'active': True, 'currentOpTime': '2024-06-15T20:49:23.229+00:00', 'threaded': True, 'opid': 'rs-shard-03:173615', 'secs_running': 2, 'microsecs_running': 2779967, 'op': 'command', 'ns': 'admin.$cmd', 'command': {'isMaster': 1, 'maxAwaitTimeMS': 10000, 'topologyVersion': {'processId': ObjectId('666ddc296f28ec37c0063331'), 'counter': 6}, 'internalClient': {'minWireVersion': 17, 'maxWireVersion': 17}, 'maxTimeMSOpOnly': 20000, '$db': 'admin'}, 'numYields': 0, 'waitingForLatch': {'timestamp': datetime.datetime(2024, 6, 15, 20, 49, 20, 554000), 'captureName': 'AnonymousLockable'}, 'locks': {}, 'waitingForLock': False, 'lockStats': {}, 'waitingForFlowControl': False, 'flowControlStats': {}}
...
...

Total number of printed operations: 13

```


## bt-mongodb-query-profiler

This script allows you to query MongoDB's profiling data and provides detailed statistics about query performance. It supports filtering based on log levels and allows sorting and limiting the output.

Features:

- Filter by Log Level: Supports various log levels including panic, fatal, error, warn, info, and debug.
- Detailed Statistics: Provides detailed statistics for each query including execution time, documents scanned, documents returned, and bytes received.
- Sorting and Limiting: Allows sorting the output based on various fields and limiting the number of queries displayed.


### Usage
```
python3 bt-mongodb-query-profiler --help

usage: bt-mongodb-query-profiler [-h] [-u USERNAME] [-p PASSWORD] [-a AUTH_DB] -d DATABASE [--mongo_host MONGO_HOST] [-l LOG_LEVEL] [-n LIMIT] [-o ORDER_BY]

MongoDB Profiling Query Script

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Specifies the user name for connecting to a server with authentication enabled.
  -p PASSWORD, --password PASSWORD
                        Specifies the password to use when connecting to a server with authentication enabled.
  -a AUTH_DB, --auth_db AUTH_DB
                        Specifies the database used to establish credentials and privileges with a MongoDB server.
  -d DATABASE, --database DATABASE
                        Specifies which database to profile
  --mongo_host MONGO_HOST
                        Specifies the MongoDB host
  -l LOG_LEVEL, --log_level LOG_LEVEL
                        Specifies the log level: panic, fatal, error, warn, info, debug
  -n LIMIT, --limit LIMIT
                        Limits the number of queries to show. Default : everything
  -o ORDER_BY, --order_by ORDER_BY
                        Specifies the sorting order using fields: count, ratio, query-time, docs-scanned, docs-returned

```
#### Example
```
python3 bt-mongodb-query-profiler --log_level debug --limit 2 --database testdb --order_by query_time

2024-06-15 20:53:58,558 - INFO - Connecting to MongoDB with URI: mongodb://localhost:27017
2024-06-15 20:53:58,565 - DEBUG - Query: {'op': {'$nin': ['getmore', 'delete']}}
2024-06-15 20:53:58,565 - DEBUG - Using sort order: [('query_time', 1)]
2024-06-15 20:53:58,565 - DEBUG - {"message": "Server selection started", "selector": "Primary()", "operation": "find", "topologyDescription": "<TopologyDescription id: 666dff661d02b7aa9f3994e8, topology_type: Sharded, servers: [<ServerDescription ('localhost', 27017) server_type: Mongos, rtt: 0.001359333997243084>]>", "clientId": {"$oid": "666dff661d02b7aa9f3994e8"}}
2024-06-15 20:53:58,565 - DEBUG - {"message": "Server selection succeeded", "selector": "Primary()", "operation": "find", "topologyDescription": "<TopologyDescription id: 666dff661d02b7aa9f3994e8, topology_type: Sharded, servers: [<ServerDescription ('localhost', 27017) server_type: Mongos, rtt: 0.001359333997243084>]>", "clientId": {"$oid": "666dff661d02b7aa9f3994e8"}, "serverHost": "localhost", "serverPort": 27017}
```

----

## bt-mongodb-sharded-size-printer & bt-mongodb-replciated-size-printer

This script allows you to check total Disk, Document, Storage and Index sizes on both Sharded & Replicated clusters.

### Usage
```
python3 bt-mongodb-sharded-size-printer --help

usage: bt-mongodb-sharded-size-printer [-h] [--user USER] [--password PASSWORD] [--host HOST] [--port PORT]

Connect to MongoDB and list databases and collection sizes.

optional arguments:
  -h, --help           show this help message and exit
  --user USER          MongoDB user
  --password PASSWORD  MongoDB password
  --host HOST          MongoDB host
  --port PORT          MongoDB port


```
#### Example
```
python3 bt-mongodb-sharded-size-printer

Database: MyDatabase
+----------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
|   Collection   | Documents | Storage Size (bytes) | Indexes | Index Size (bytes) | Total Data Size | Total Index Size | Avg Obj Size |
+----------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
| system.profile |     27    |        50563         |    0    |         0          |      45056      |        0         |    1872.0    |
|  MyCollection  |     2     |          74          |    4    |       65536        |      28672      |      65536       |     37.0     |
|    products    |     1     |          37          |    1    |       20480        |      20480      |      20480       |     37.0     |
+----------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
Database: admin
+----------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
|   Collection   | Documents | Storage Size (bytes) | Indexes | Index Size (bytes) | Total Data Size | Total Index Size | Avg Obj Size |
+----------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
| system.version |     1     |          59          |    1    |       20480        |      20480      |      20480       |     59.0     |
|  system.keys   |     2     |         170          |    1    |       20480        |      20480      |      20480       |     85.0     |
+----------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
Database: config
+----------------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
|      Collection      | Documents | Storage Size (bytes) | Indexes | Index Size (bytes) | Total Data Size | Total Index Size | Avg Obj Size |
+----------------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
|        shards        |     3     |         387          |    2    |       40960        |      20480      |      40960       |    129.0     |
|        mongos        |     2     |         268          |    1    |       20480        |      36864      |      20480       |    134.0     |
|      databases       |     3     |         401          |    1    |       36864        |      36864      |      36864       |    133.0     |
|      changelog       |    3759   |       1830442        |    1    |       356352       |      532480     |      356352      |    486.0     |
|     transactions     |     0     |          0           |    2    |       16384        |      24576      |      16384       |     0.0      |
|  system.indexBuilds  |     0     |          0           |    1    |        4096        |       4096      |       4096       |     0.0      |
|   image_collection   |     0     |          0           |    1    |        4096        |       4096      |       4096       |     0.0      |
|         tags         |     0     |          0           |    3    |       12288        |       4096      |      12288       |     0.0      |
|        locks         |     4     |         768          |    3    |       110592       |      36864      |      110592      |    192.0     |
| reshardingOperations |     0     |          0           |    2    |        8192        |       4096      |       8192       |     0.0      |
|   system.preimages   |     0     |          0           |    0    |         0          |       4096      |        0         |     0.0      |
|      lockpings       |     4     |         155          |    2    |       57344        |      36864      |      57344       |     38.0     |
|      actionlog       |    682    |        201190        |    1    |       106496       |      106496     |      106496      |    295.0     |
|     collections      |     2     |         441          |    1    |       36864        |      36864      |      36864       |    220.0     |
|       version        |     1     |          83          |    1    |       20480        |      20480      |      20480       |     83.0     |
|        chunks        |    1030   |        286086        |    4    |       438272       |      126976     |      438272      |    277.0     |
|      migrations      |     0     |          0           |    2    |        8192        |       4096      |       8192       |     0.0      |
+----------------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
Database: testdb
+------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
| Collection | Documents | Storage Size (bytes) | Indexes | Index Size (bytes) | Total Data Size | Total Index Size | Avg Obj Size |
+------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
|  test_col  |     0     |          0           |    3    |       12288        |       4096      |      12288       |     0.0      |
+------------+-----------+----------------------+---------+--------------------+-----------------+------------------+--------------+
Total Documents: 5523
Total Data Size: 1.1 MiB
Total Index Size: 1.4 MiB
RAM Headroom: 2.3 KiB
RAM Used: 59 Bytes (2.4%)
```


## bt-mongodb-replicated-heartbeat-profiler & bt-mongodb-sharded-heartbeat-profiler

This Python script allows you to monitor the heartbeat status of MongoDB clusters, both sharded and replicated. These scripts connect to the primary node(s) of each shard or replica set and run the replSetGetStatus command to gather and analyze heartbeat information.

Features:

- Sharded Cluster Monitoring: Checks the heartbeat status of each shard in a MongoDB sharded cluster.
- Replicated Cluster Monitoring: Checks the heartbeat status of a MongoDB replicated cluster.
- Detailed Heartbeat Information: Gathers and displays detailed information about the state, health, uptime, and last heartbeat messages of each member.
- Issue Detection: Analyzes the heartbeat data to detect potential issues and provides suggestions for troubleshooting.
- Flexible Configuration: Allows configuration of MongoDB connection details via command line arguments.

### Usage
```
python3 bt-mongodb-sharded-heartbeat-profiler --help

usage: bt-mongodb-sharded-heartbeat-profiler [-h] [--host HOST] [--port PORT] [--username USERNAME] [--password PASSWORD]

Check heartbeat status in a MongoDB sharded cluster.

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          MongoDB host (default: localhost)
  --port PORT          MongoDB port (default: 27017)
  --username USERNAME  MongoDB username
  --password PASSWORD  MongoDB password


```
#### Example
```
python3 bt-mongodb-sharded-heartbeat-profiler

Checking heartbeat for shard: rs-shard-01 at shard01-a:27017
Checking heartbeat for shard: rs-shard-02 at shard02-a:27017
Checking heartbeat for shard: rs-shard-03 at shard03-a:27017
Replication heartbeat information:

Member: shard01-a:27017
  state: PRIMARY
  health: 1.0
  uptime: 9715
  lastHeartbeat: N/A
  lastHeartbeatRecv: N/A
  lastHeartbeatMessage: 

Member: shard01-b:27017
  state: SECONDARY
  health: 1.0
  uptime: 9700
  lastHeartbeat: 2024-06-15 21:05:30.016000
  lastHeartbeatRecv: 2024-06-15 21:05:30.914000
  lastHeartbeatMessage: 

Member: shard01-c:27017
  state: SECONDARY
  health: 1.0
  uptime: 9701
  lastHeartbeat: 2024-06-15 21:05:30.016000
  lastHeartbeatRecv: 2024-06-15 21:05:30.012000
  lastHeartbeatMessage: 

Member: shard02-a:27017
  state: SECONDARY
  health: 1.0
  uptime: 9701
  lastHeartbeat: 2024-06-15 21:05:31.126000
  lastHeartbeatRecv: 2024-06-15 21:05:31.126000
  lastHeartbeatMessage: 

Member: shard02-b:27017
  state: PRIMARY
  health: 1.0
  uptime: 9716
  lastHeartbeat: N/A
  lastHeartbeatRecv: N/A
  lastHeartbeatMessage: 

Member: shard02-c:27017
  state: SECONDARY
  health: 1.0
  uptime: 9699
  lastHeartbeat: 2024-06-15 21:05:30.977000
  lastHeartbeatRecv: 2024-06-15 21:05:31.126000
  lastHeartbeatMessage: 

Member: shard03-a:27017
  state: PRIMARY
  health: 1.0
  uptime: 9714
  lastHeartbeat: N/A
  lastHeartbeatRecv: N/A
  lastHeartbeatMessage: 

Member: shard03-b:27017
  state: SECONDARY
  health: 1.0
  uptime: 9699
  lastHeartbeat: 2024-06-15 21:05:29.567000
  lastHeartbeatRecv: 2024-06-15 21:05:30.915000
  lastHeartbeatMessage: 

Member: shard03-c:27017
  state: SECONDARY
  health: 1.0
  uptime: 9701
  lastHeartbeat: 2024-06-15 21:05:29.560000
  lastHeartbeatRecv: 2024-06-15 21:05:30.305000
  lastHeartbeatMessage: 

No issues found with heartbeat.


```

## bt-system-summary

This scripts allows you to print operating system summary

### Usage
```
python3 bt-system-summary

```
#### Example
```
python3 bt-system-summary


# System Summary ##########################
Date         | Sat Jun 15 21:10:23 UTC 2024
Hostname     | f87ace4a3ab1
Uptime       | 21:10:23 up 1 day,  6:20,  0 users,  load average: 3.65, 3.60, 4.01
Platform     | Linux 6.6.31-linuxkit aarch64
Release      | PRETTY_NAME="Ubuntu 20.04.5 LTS"
Kernel       | No SELinux detected
Architecture | No virtualization detected
# Processor ##########################
Processors | physical = 4, cores = 8, virtual = 8, hyperthreading = False
Speeds     |
Models     | aarch64
Caches     |
# Memory ##########################
Total      | 11Gi
Free       | 230Mi
Used       | physical = 7.3Gi, swap allocated = , swap used = , virtual = 7.3Gi
Shared     | 10936
0
0 kB
Buffers    | 313156 kB
Caches     | 3378120
0 kB
Dirty      | 2948 kB
UsedRSS    | 10.9 MB
Swappiness | 60
# Mounted Filesystems ##########################
Filesystem |       Size       Used Type       Opts       Mountpoint
/dev/vda1  | 62.7G   64% ext4       rw,relatime,discard /data/configdb
/dev/vda1  | 62.7G   64% ext4       rw,relatime,discard /data/db
/dev/vda1  | 62.7G   64% ext4       rw,relatime,discard /etc/resolv.conf
/dev/vda1  | 62.7G   64% ext4       rw,relatime,discard /etc/hostname
/dev/vda1  | 62.7G   64% ext4       rw,relatime,discard /etc/hosts
# Disk Schedulers And Queue Size ##########################
Block Device | Scheduler      Queue Size
ram0         | N/A                   N/A
ram1         | N/A                   N/A
ram2         | N/A                   N/A
ram3         | N/A                   N/A
ram4         | N/A                   N/A
ram5         | N/A                   N/A
ram14        | N/A                   N/A
ram15        | N/A                   N/A
loop0        | on                    128
loop1        | on                    128
loop2        | on                    128
loop3        | on                    128
loop4        | on                    128
loop5        | on                    128
loop6        | on                    128
loop7        | on                    128
nbd0         | q-deadlin             256
nbd1         | q-deadlin             256
nbd2         | q-deadlin             256
# Disk Partioning ##########################
# Kernel Inode State ##########################
Parameter    | Value
dentry-state | 587507	333994	45	0	60965	0
file-nr      | 222272	0	1223082
inode-nr     | 525680	365
# Kernel Inode State ##########################
/bin/sh: 1: lvdisplay: not found
/bin/sh: 1: vgdisplay: not found
/bin/sh: 1: lspci: not found
# LVM Volumes ################################################
Controller not detected
# LVM Volume Groups ##########################################
Controller not detected
# RAID Controller ############################################
  Controller | Controller not detected
# Network Config ##########################
 Port Range | 32768	60999
# Interface Statistics  ##########################
interface    rx_bytes rx_packets  rx_errors   tx_bytes tx_packets  tx_errors
======================================================================
lo            7398421       4712          0    7398421       4712          0
tunl0               0          0          0          0          0          0
gre0                0          0          0          0          0          0
gretap0             0          0          0          0          0          0
erspan0             0          0          0          0          0          0
ip_vti0             0          0          0          0          0          0
ip6_vti0            0          0          0          0          0          0
sit0                0          0          0          0          0          0
ip6tnl0             0          0          0          0          0          0
ip6gre0             0          0          0          0          0          0
eth0        121429368     103867          0    8952118      73318          0
# Network Connections  ##########################
Connections from remote IP addresses
  172.18.0.11: 3
  172.18.0.13: 4
  172.18.0.15: 5

Connections to local IP addresses

  0.0.0.0: 1
  127.0.0.11: 2

Connections to top 10 local ports
  37726: 1
  52110: 1
  55752: 1
  33364: 1
  48712: 1
  58740: 1
  51098: 1
  44720: 1
  42416: 1
  33744: 1

States of connections
  ESTABLISHED: 46
  LISTEN: 2
  NONE: 1
# Transparent Huge Pages Status ##########################
Transparent Huge Pages status is unknown or not applicable.


```

## bt-system-summary

This script will suggest you about operating system parameters and values


### Usage
```
python3 bt-system-tuning-adviser 

```
#### Example
```
THP:  [always] madvise never
THP status: Enable
It is recommended to disable THP for MongoDB
Current Transparent Huge Pages (THP) status: Enable
************************************************************************
Suggestion : Reduce Swappiness: Set the swappiness value to a lower number (like 10) to avoid using swap space excessively. Use sudo sysctl vm.swappiness=10 and follow document to make changes persistent after reboot.
Current Swappiness setting:  60
************************************************************************
Dirty Ratio: 20
Dirty Background Ratio: 10
The default values may not be suitable for MongoDB's write-heavy workload, so it is recommended to increase them.
************************************************************************
Disable 'atime' Updates:
noatime option for mounted drives to reduce unnecessary write operations
Suggestion: Include 'noatime' option for mounted drives in /etc/fstab
************************************************************************
Current File Descriptors: 1048576
Default maximum number of open file descriptors in Linux may not be sufficient for MongoDB, which performs a large number of disk I/O operations.
To increase  open file descriptors in Linux - Edit /etc/security/limits.conf , follow official linux document for applying change.
************************************************************************
net/ipv4/tcp_window_scaling =  1
net/ipv4/tcp_sack =  1
net/ipv4/tcp_timestamps =  1
net/ipv4/tcp_fin_timeout =  60
net/ipv4/tcp_tw_reuse =  2
net/ipv4/tcp_tw_recycle =  Not found
MongoDB is a network-intensive application, and tuning TCP parameters can improve its performance
************************************************************************
Linux kernel parameter settings:  
Current value of net.core.somaxconn: 4096
No action needed: net.core.somaxconn is already set to an optimal value or higher.
Current value of net.ipv4.tcp_max_syn_backlog: 1024
Suggestion: Increase net.ipv4.tcp_max_syn_backlog to 4096 for better performance.
************************************************************************
The current I/O scheduler for vdc is: none [mq-deadline] kyber
The current I/O scheduler for vdc is: mq-deadline
It is recommended to use the 'noop' or 'deadline' IO scheduler for MongoDB.
************************************************************************
Overcommit Setting :
Current overcommit_memory value: 1
Overcommit memory setting is correctly configured (0 or 1).
************************************************************************
CPU Scaling Governor :
No scaling governor files found. CPU frequency scaling may not be supported or enabled.


```

-----
## bt-mongodb-cpu-and-mem-killer-processess

This script allows you detect cpu and mem killer processess.


### Usage
```
python3 bt-mongodb-cpu-and-mem-killer-processess.py --help

usage: test [-h] [--host HOST] [--port PORT] [--user USER] [--password PASSWORD] [--check {mem,cpu}] [--check-both] [--order-by {asc,desc}] [--limit LIMIT] [--all-databases]
            [--ignore-databases [IGNORE_DATABASES [IGNORE_DATABASES ...]]]

Check MongoDB running operations consuming most CPU and RAM.

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           MongoDB host (default: localhost)
  --port PORT           MongoDB port (default: 27017)
  --user USER           MongoDB user (default: None)
  --password PASSWORD   MongoDB password (default: None)
  --check {mem,cpu}     Check memory or CPU usage
  --check-both          Check both memory and CPU usage
  --order-by {asc,desc}
                        Order results by ascending or descending secs_running (default: descending)
  --limit LIMIT         Limit the number of results
  --all-databases       Include operations from all databases
  --ignore-databases [IGNORE_DATABASES [IGNORE_DATABASES ...]]
                        Databases to ignore when using --all-databases 

```
#### Example
```
python3 test --check-both --all-databases --limit 2 --order-by desc
{'type': 'op', 'host': '4ef314225763:27017', 'desc': 'conn544', 'connectionId': 544, 'client': '172.18.0.8:54054', 'appName': 'OplogFetcher', 'clientMetadata': {'application': {'name': 'OplogFetcher'}, 'driver': {'name': 'MongoDB Internal Client', 'version': '6.0.1'}, 'os': {'type': 'Linux', 'name': 'Ubuntu', 'architecture': 'aarch64', 'version': '20.04'}}, 'active': True, 'currentOpTime': '2024-06-16T20:08:48.871+00:00', 'threaded': True, 'opid': 194705, 'secs_running': 3, 'microsecs_running': 3663326, 'op': 'getmore', 'ns': 'local.oplog.rs', 'command': {'getMore': 1982380187062395607, 'collection': 'oplog.rs', 'batchSize': 13981010, 'maxTimeMS': 5000, 'term': 13, 'lastKnownCommittedOpTime': {'ts': Timestamp(1718562458, 1), 't': 12}, '$db': 'local', '$replData': 1, '$oplogQueryData': 1, '$readPreference': {'mode': 'secondaryPreferred'}, '$clusterTime': {'clusterTime': Timestamp(1718562622, 2), 'signature': {'hash': b'\xb6\xbd31\xc0\xe6\x08\xed\x96m\x7f\x0ew\xc6\xa1\x00\xd9\x99G\xb8', 'keyId': 7379686634180050968}}, '$configTime': Timestamp(1718562622, 1), '$topologyTime': Timestamp(1718217211, 6)}, 'planSummary': 'COLLSCAN', 'cursor': {'cursorId': 1982380187062395607, 'createdDate': datetime.datetime(2024, 6, 16, 18, 30, 23, 341000), 'lastAccessDate': datetime.datetime(2024, 6, 16, 20, 8, 45, 207000), 'nDocsReturned': 373, 'nBatchesReturned': 1132, 'noCursorTimeout': False, 'tailable': True, 'awaitData': True, 'originatingCommand': {'find': 'oplog.rs', 'filter': {'ts': {'$gte': Timestamp(1718562612, 1)}}, 'batchSize': 13981010, 'tailable': True, 'awaitData': True, 'term': 13, 'maxTimeMS': 60000, 'readConcern': {'level': 'local', 'afterClusterTime': Timestamp(0, 1)}, '$db': 'local', '$replData': 1, '$oplogQueryData': 1, '$readPreference': {'mode': 'secondaryPreferred'}, '$clusterTime': {'clusterTime': Timestamp(1718562622, 2), 'signature': {'hash': b'\xb6\xbd31\xc0\xe6\x08\xed\x96m\x7f\x0ew\xc6\xa1\x00\xd9\x99G\xb8', 'keyId': 7379686634180050968}}, '$configTime': Timestamp(1718562622, 1), '$topologyTime': Timestamp(1718217211, 6)}, 'operationUsingCursorId': 194705, 'lastKnownCommittedOpTime': {'ts': Timestamp(1718568525, 1), 't': 13}}, 'numYields': 2, 'locks': {}, 'waitingForLock': False, 'lockStats': {'FeatureCompatibilityVersion': {'acquireCount': {'r': 2}}, 'Global': {'acquireCount': {'r': 2}}, 'Mutex': {'acquireCount': {'r': 1}}}, 'waitingForFlowControl': False, 'flowControlStats': {}}
...
...

```
