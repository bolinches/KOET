#  Network latency check tool

This runs a network fping tests across multiple nodes 1:1 and 1:n to obtain the mean average for all the nodes involved and compares it against a KPI.

It requires a long time to run, depending on the number of nodes. The tool estimates a runtime at startup.

Remarks:
  - Runs on RedHat 7.5/7.6 and CentOS 7.5/7.6 on ppc64le, ppc64 and x86_64
  - Python 2.7.x required, which is the default on Redhat/Centos 7.x series
  - Only standard libraries are used
  - fping must be installed on all nodes that participate in the test (it does check it)
  - SSH root passwordless access must be possible from the node that runs the tool to all the nodes that participate in the test (it does check it)
  - The minimum FPING_COUNT value for a valid test must be 500 (by default is 500 already)
  - The toll run on a number of hosts between 4 and 32 (included)
  - It generates a log directory with all the raw data output for future comparisons (not implemented yet)
  - It returns 0 if all tests are passed in all nodes, it returns an integer > 0 if any number of errors

## Prerequisites

The tool `koet.py` has two dependencies.

### Password less ssh between hosts

For password less ssh, the process is simple if you google it. However, there is an automated script at [https://github.com/vikramkhatri/sshsetup](https://github.com/vikramkhatri/sshsetup) that you can use to set up password less ssh.

### Install fping

Check if `fping` is available or not. `which fping`

If `fping` is not install, install it from epel repo.

```
yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum -y install fping
```

Repeat on all hosts.

### Prepaere hosts.json file 

Edit `hosts.json` with the IP addresses of the nodes that will participate in the test. ** Names are not allowed.**

## Help for the tool

```
# ./koet.py -h
usage: koet.py [-h] [-l KPI_LATENCY] [-c FPING_COUNT] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -l KPI_LATENCY, --latency KPI_LATENCY
                        The KPI latency value as float. The maximum required
                        value for certification is 1.0 msec
  -c FPING_COUNT, --fping_count FPING_COUNT
                        The number of fping counts to run per node and test.
                        The minimum required value for certification is 500
  -v, --version         show program's version number and exit
An output example:

```

## Run the tool
```
# ./koet.py

Welcome to KOET, version 1.7

JSON files versions:
        supported OS:           1.0
        packages:               1.0

Please use https://github.com/bolinches/KOET to get latest versions and report issues about KOET.

The purpose of KOET is to obtain IPv4 network metrics for a number of nodes.

The latency KPI value of 1.0 msec is good to certify the environment

The fping count value of 500 pings per test and node is good to certify the environment

It requires remote ssh passwordless between all nodes for user root already configured

This test is going to take at least 50 minutes to complete

This software comes with absolutely no warranty of any kind. Use it at your own risk

Do you want to continue? (y/n): y
```

At this point you can see the estimated runtime, consider using screen or alike. If you modify the number of fpings or the latency KPI you might see warning messages as below:
```
# ./koet.py -l 1.5 -c 100

Welcome to KOET, version 1.6

JSON files versions:
        supported OS:           1.0
        packages:               1.0

Please use https://github.com/bolinches/KOET to get latest versions and report issues about KOET.

The purpose of KOET is to obtain IPv4 network metrics for a number of nodes.

WARNING: The latency KPI value of 1.5 msec is too high to certify the environment

WARNING: The fping count value of 100 pings per test and node is not enough to certify the environment

It requires remote ssh passwordless between all nodes for user root already configured

This test is going to take at least 50 minutes to complete

This software comes with absolutely no warranty of any kind. Use it at your own risk

Do you want to continue? (y/n): y
```

A successful run within the KPI range of test requirements and results, would look similar to the below output:
```
OK: Red Hat Enterprise Linux Server 7.6 is a supported OS for this tool

OK: SSH with node 10.10.16.17 works
OK: SSH with node 10.10.16.16 works
OK: SSH with node 10.10.16.15 works
OK: SSH with node 10.10.16.13 works
OK: SSH with node 10.10.16.10 works
OK: SSH with node 10.10.11.35 works

Checking packages install status:

OK: on host 10.10.16.17 the fping installation status is as expected
OK: on host 10.10.16.16 the fping installation status is as expected
OK: on host 10.10.16.15 the fping installation status is as expected
OK: on host 10.10.16.13 the fping installation status is as expected
OK: on host 10.10.16.10 the fping installation status is as expected
OK: on host 10.10.11.35 the fping installation status is as expected

Starting ping run from 10.10.16.17 to each node
        Starting ping from 10.10.16.17 to 10.10.16.16
        Ping from 10.10.16.17 to 10.10.16.16 completed
        Starting ping from 10.10.16.17 to 10.10.16.15
        Ping from 10.10.16.17 to 10.10.16.15 completed
        Starting ping from 10.10.16.17 to 10.10.16.13
        Ping from 10.10.16.17 to 10.10.16.13 completed
        Starting ping from 10.10.16.17 to 10.10.16.10
        Ping from 10.10.16.17 to 10.10.16.10 completed
        Starting ping from 10.10.16.17 to 10.10.11.35
        Ping from 10.10.16.17 to 10.10.11.35 completed
Ping run from 10.10.16.17 to each node completed

Starting ping run from 10.10.16.16 to each node
        Starting ping from 10.10.16.16 to 10.10.16.17
        Ping from 10.10.16.16 to 10.10.16.17 completed
        Starting ping from 10.10.16.16 to 10.10.16.15
        Ping from 10.10.16.16 to 10.10.16.15 completed
        Starting ping from 10.10.16.16 to 10.10.16.13
        Ping from 10.10.16.16 to 10.10.16.13 completed
        Starting ping from 10.10.16.16 to 10.10.16.10
        Ping from 10.10.16.16 to 10.10.16.10 completed
        Starting ping from 10.10.16.16 to 10.10.11.35
        Ping from 10.10.16.16 to 10.10.11.35 completed
Ping run from 10.10.16.16 to each node completed

Starting ping run from 10.10.16.15 to each node
        Starting ping from 10.10.16.15 to 10.10.16.17
        Ping from 10.10.16.15 to 10.10.16.17 completed
        Starting ping from 10.10.16.15 to 10.10.16.16
        Ping from 10.10.16.15 to 10.10.16.16 completed
        Starting ping from 10.10.16.15 to 10.10.16.13
        Ping from 10.10.16.15 to 10.10.16.13 completed
        Starting ping from 10.10.16.15 to 10.10.16.10
        Ping from 10.10.16.15 to 10.10.16.10 completed
        Starting ping from 10.10.16.15 to 10.10.11.35
        Ping from 10.10.16.15 to 10.10.11.35 completed
Ping run from 10.10.16.15 to each node completed

Starting ping run from 10.10.16.13 to each node
        Starting ping from 10.10.16.13 to 10.10.16.17
        Ping from 10.10.16.13 to 10.10.16.17 completed
        Starting ping from 10.10.16.13 to 10.10.16.16
        Ping from 10.10.16.13 to 10.10.16.16 completed
        Starting ping from 10.10.16.13 to 10.10.16.15
        Ping from 10.10.16.13 to 10.10.16.15 completed
        Starting ping from 10.10.16.13 to 10.10.16.10
        Ping from 10.10.16.13 to 10.10.16.10 completed
        Starting ping from 10.10.16.13 to 10.10.11.35
        Ping from 10.10.16.13 to 10.10.11.35 completed
Ping run from 10.10.16.13 to each node completed

Starting ping run from 10.10.16.10 to each node
        Starting ping from 10.10.16.10 to 10.10.16.17
        Ping from 10.10.16.10 to 10.10.16.17 completed
        Starting ping from 10.10.16.10 to 10.10.16.16
        Ping from 10.10.16.10 to 10.10.16.16 completed
        Starting ping from 10.10.16.10 to 10.10.16.15
        Ping from 10.10.16.10 to 10.10.16.15 completed
        Starting ping from 10.10.16.10 to 10.10.16.13
        Ping from 10.10.16.10 to 10.10.16.13 completed
        Starting ping from 10.10.16.10 to 10.10.11.35
        Ping from 10.10.16.10 to 10.10.11.35 completed
Ping run from 10.10.16.10 to each node completed

Starting ping run from 10.10.11.35 to each node
        Starting ping from 10.10.11.35 to 10.10.16.17
        Ping from 10.10.11.35 to 10.10.16.17 completed
        Starting ping from 10.10.11.35 to 10.10.16.16
        Ping from 10.10.11.35 to 10.10.16.16 completed
        Starting ping from 10.10.11.35 to 10.10.16.15
        Ping from 10.10.11.35 to 10.10.16.15 completed
        Starting ping from 10.10.11.35 to 10.10.16.13
        Ping from 10.10.11.35 to 10.10.16.13 completed
        Starting ping from 10.10.11.35 to 10.10.16.10
        Ping from 10.10.11.35 to 10.10.16.10 completed
Ping run from 10.10.11.35 to each node completed

Starting ping run from 10.10.16.17 to all nodes
Ping run from 10.10.16.17 to all nodes completed

Starting ping run from 10.10.16.16 to all nodes
Ping run from 10.10.16.16 to all nodes completed

Starting ping run from 10.10.16.15 to all nodes
Ping run from 10.10.16.15 to all nodes completed

Starting ping run from 10.10.16.13 to all nodes
Ping run from 10.10.16.13 to all nodes completed

Starting ping run from 10.10.16.10 to all nodes
Ping run from 10.10.16.10 to all nodes completed

Starting ping run from 10.10.11.35 to all nodes
Ping run from 10.10.11.35 to all nodes completed

Loading ping results of 10.10.16.17 to each node
        Loading from 10.10.16.17 to 10.10.16.16
        Loaded from 10.10.16.17 to 10.10.16.16 completed
        Loading from 10.10.16.17 to 10.10.16.15
        Loaded from 10.10.16.17 to 10.10.16.15 completed
        Loading from 10.10.16.17 to 10.10.16.13
        Loaded from 10.10.16.17 to 10.10.16.13 completed
        Loading from 10.10.16.17 to 10.10.16.10
        Loaded from 10.10.16.17 to 10.10.16.10 completed
        Loading from 10.10.16.17 to 10.10.11.35
        Loaded from 10.10.16.17 to 10.10.11.35 completed
Load ping results from 10.10.16.17 to each node completed

Loading ping results of 10.10.16.16 to each node
        Loading from 10.10.16.16 to 10.10.16.17
        Loaded from 10.10.16.16 to 10.10.16.17 completed
        Loading from 10.10.16.16 to 10.10.16.15
        Loaded from 10.10.16.16 to 10.10.16.15 completed
        Loading from 10.10.16.16 to 10.10.16.13
        Loaded from 10.10.16.16 to 10.10.16.13 completed
        Loading from 10.10.16.16 to 10.10.16.10
        Loaded from 10.10.16.16 to 10.10.16.10 completed
        Loading from 10.10.16.16 to 10.10.11.35
        Loaded from 10.10.16.16 to 10.10.11.35 completed
Load ping results from 10.10.16.16 to each node completed

Loading ping results of 10.10.16.15 to each node
        Loading from 10.10.16.15 to 10.10.16.17
        Loaded from 10.10.16.15 to 10.10.16.17 completed
        Loading from 10.10.16.15 to 10.10.16.16
        Loaded from 10.10.16.15 to 10.10.16.16 completed
        Loading from 10.10.16.15 to 10.10.16.13
        Loaded from 10.10.16.15 to 10.10.16.13 completed
        Loading from 10.10.16.15 to 10.10.16.10
        Loaded from 10.10.16.15 to 10.10.16.10 completed
        Loading from 10.10.16.15 to 10.10.11.35
        Loaded from 10.10.16.15 to 10.10.11.35 completed
Load ping results from 10.10.16.15 to each node completed

Loading ping results of 10.10.16.13 to each node
        Loading from 10.10.16.13 to 10.10.16.17
        Loaded from 10.10.16.13 to 10.10.16.17 completed
        Loading from 10.10.16.13 to 10.10.16.16
        Loaded from 10.10.16.13 to 10.10.16.16 completed
        Loading from 10.10.16.13 to 10.10.16.15
        Loaded from 10.10.16.13 to 10.10.16.15 completed
        Loading from 10.10.16.13 to 10.10.16.10
        Loaded from 10.10.16.13 to 10.10.16.10 completed
        Loading from 10.10.16.13 to 10.10.11.35
        Loaded from 10.10.16.13 to 10.10.11.35 completed
Load ping results from 10.10.16.13 to each node completed

Loading ping results of 10.10.16.10 to each node
        Loading from 10.10.16.10 to 10.10.16.17
        Loaded from 10.10.16.10 to 10.10.16.17 completed
        Loading from 10.10.16.10 to 10.10.16.16
        Loaded from 10.10.16.10 to 10.10.16.16 completed
        Loading from 10.10.16.10 to 10.10.16.15
        Loaded from 10.10.16.10 to 10.10.16.15 completed
        Loading from 10.10.16.10 to 10.10.16.13
        Loaded from 10.10.16.10 to 10.10.16.13 completed
        Loading from 10.10.16.10 to 10.10.11.35
        Loaded from 10.10.16.10 to 10.10.11.35 completed
Load ping results from 10.10.16.10 to each node completed

Loading ping results of 10.10.11.35 to each node
        Loading from 10.10.11.35 to 10.10.16.17
        Loaded from 10.10.11.35 to 10.10.16.17 completed
        Loading from 10.10.11.35 to 10.10.16.16
        Loaded from 10.10.11.35 to 10.10.16.16 completed
        Loading from 10.10.11.35 to 10.10.16.15
        Loaded from 10.10.11.35 to 10.10.16.15 completed
        Loading from 10.10.11.35 to 10.10.16.13
        Loaded from 10.10.11.35 to 10.10.16.13 completed
        Loading from 10.10.11.35 to 10.10.16.10
        Loaded from 10.10.11.35 to 10.10.16.10 completed
Load ping results from 10.10.11.35 to each node completed

Loading ping results of 10.10.16.17 to all nodes
Load ping results from 10.10.16.17 to all nodes completed

Loading ping results of 10.10.16.16 to all nodes
Load ping results from 10.10.16.16 to all nodes completed

Loading ping results of 10.10.16.15 to all nodes
Load ping results from 10.10.16.15 to all nodes completed

Loading ping results of 10.10.16.13 to all nodes
Load ping results from 10.10.16.13 to all nodes completed

Loading ping results of 10.10.16.10 to all nodes
Load ping results from 10.10.16.10 to all nodes completed

Loading ping results of 10.10.11.35 to all nodes
Load ping results from 10.10.11.35 to all nodes completed

Results for test 1:1
OK: on host 10.10.16.17 the 1:1 average latency is 0.47 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.17 the 1:1 maximum latency is 0.6 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.16.17 the 1:1 minimum latency is 0.4 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.17 the 1:1 standard deviation of latency is 0.07 msec. Which is lower than the KPI of 0.33 msec

OK: on host 10.10.16.16 the 1:1 average latency is 0.35 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.16 the 1:1 maximum latency is 0.39 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.16.16 the 1:1 minimum latency is 0.33 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.16 the 1:1 standard deviation of latency is 0.02 msec. Which is lower than the KPI of 0.33 msec

OK: on host 10.10.16.15 the 1:1 average latency is 0.52 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.15 the 1:1 maximum latency is 0.73 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.16.15 the 1:1 minimum latency is 0.4 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.15 the 1:1 standard deviation of latency is 0.12 msec. Which is lower than the KPI of 0.33 msec

OK: on host 10.10.16.13 the 1:1 average latency is 0.41 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.13 the 1:1 maximum latency is 0.46 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.16.13 the 1:1 minimum latency is 0.33 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.13 the 1:1 standard deviation of latency is 0.05 msec. Which is lower than the KPI of 0.33 msec

OK: on host 10.10.16.10 the 1:1 average latency is 0.51 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.10 the 1:1 maximum latency is 0.58 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.16.10 the 1:1 minimum latency is 0.46 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.10 the 1:1 standard deviation of latency is 0.04 msec. Which is lower than the KPI of 0.33 msec

OK: on host 10.10.11.35 the 1:1 average latency is 0.52 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.11.35 the 1:1 maximum latency is 0.59 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.11.35 the 1:1 minimum latency is 0.45 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.11.35 the 1:1 standard deviation of latency is 0.05 msec. Which is lower than the KPI of 0.33 msec

Results for test 1:n
OK: on host 10.10.16.17 the 1:n average latency is 0.55 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.17 the 1:n maximum latency is 0.98 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.16.17 the 1:n minimum latency is 0.27 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.17 the 1:n standard deviation of latency is 0.08 msec. Which is lower than the KPI of 0.33 msec

OK: on host 10.10.16.16 the 1:n average latency is 0.49 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.16 the 1:n maximum latency is 0.98 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.16.16 the 1:n minimum latency is 0.27 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.16 the 1:n standard deviation of latency is 0.09 msec. Which is lower than the KPI of 0.33 msec

OK: on host 10.10.16.15 the 1:n average latency is 0.6 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.15 the 1:n maximum latency is 1.55 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.16.15 the 1:n minimum latency is 0.27 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.15 the 1:n standard deviation of latency is 0.19 msec. Which is lower than the KPI of 0.33 msec

OK: on host 10.10.16.13 the 1:n average latency is 0.56 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.13 the 1:n maximum latency is 1.55 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.16.13 the 1:n minimum latency is 0.25 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.13 the 1:n standard deviation of latency is 0.18 msec. Which is lower than the KPI of 0.33 msec

OK: on host 10.10.16.10 the 1:n average latency is 0.53 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.10 the 1:n maximum latency is 1.55 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.16.10 the 1:n minimum latency is 0.25 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.16.10 the 1:n standard deviation of latency is 0.17 msec. Which is lower than the KPI of 0.33 msec

OK: on host 10.10.11.35 the 1:n average latency is 0.52 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.11.35 the 1:n maximum latency is 1.55 msec. Which is lower than the KPI of 2.0 msec
OK: on host 10.10.11.35 the 1:n minimum latency is 0.25 msec. Which is lower than the KPI of 1.0 msec
OK: on host 10.10.11.35 the 1:n standard deviation of latency is 0.16 msec. Which is lower than the KPI of 0.33 msec


The summary of this run:

        The 1:1 fping latency was successful in all nodes
        The 1:n fping average latency was successful in all nodes

OK: All tests had been passed
OK: You can proceed with the next steps
```
