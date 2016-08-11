# server_cellsCycle
Elastic Distributed Shared Memory In The Cloud

# Project’s needs

## Not functional
* You can choose the programming language
*  You can use support libraries and tools to develop your project 
*  System/service with configurable parameters (no hard-coded!)–  Through a configuration file/service 
*  You must test all the functionalities of your developed system/service and present and discuss the testing results in the project report
*  System/service supports multiple, autonomous entities contending for shared resources
*  System/service supports real-time updates to some form of shared state
*  System/service state should be distributed across multiple client or server nodes
–  The only allowed centralized service can be one that supports users logging on, adding or removing clients or servers, and other housekeeping tasks 
*  System/service scalability and elasticity
*  System/service fault tolerance, in particular system/ service continues operation even if one of the participant nodes crashes (optionally, recovers the state of a crashed node so that it can resume operation)

## Functional
* Realize a distributed shared memory system that supports application scale-up and
scale-down
*  Design a totally elastic solution: add new nodes and remove existing nodes without restarting other nodes in the system
*  Scale-down can be challenging due to need to perform state reintegration
*  Handle node failover
*  Support at least two consistency models
*  Some examples: 
https://github.com/memcached/memcached
https://github.com/hazelcast/hazelcast
