#!/usr/bin/python
import json
import os
import sys
import socket
import datetime
import subprocess
import platform
import shlex
from decimal import Decimal
import argparse
import operator
from math import sqrt
from functools import reduce

# Colorful constants
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
NOCOLOR = '\033[0m'

# KPI + runtime acceptance values
MAX_AVG_LATENCY = 1.00  # Acceptance value should be 1 msec or less
FPING_COUNT = 500  # Acceptance value should be 500 or more

# GITHUB URL
GIT_URL = "https://github.com/bolinches/KOET"

# devnull redirect destination
DEVNULL = open(os.devnull, 'w')

# This script version, independent from the JSON versions
KOET_VERSION = "1.8"


def load_json(json_file_str):
    # Loads  JSON into a dictionary or quits the program if it cannot. Future
    # might add a try to donwload the JSON if not available before quitting
    try:
        with open(json_file_str, "r") as json_file:
            json_variable = json.load(json_file)
            return json_variable
    except Exception:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "Cannot open JSON file: " + json_file_str)


def estimate_runtime(hosts_dictionary, fping_count):
    number_of_hosts = len(hosts_dictionary)
    estimated_runtime = number_of_hosts * (number_of_hosts - 1) * fping_count
    # minutes we always return 2 even for short test runs
    return max((estimated_runtime / 60), 2)


def parse_arguments():
    parser = argparse.ArgumentParser()
    # We include number of runs and KPI as optional arguments
    parser.add_argument(
        '-l',
        '--latency',
        action='store',
        dest='max_avg_latency',
        help='The KPI latency value as float. ' +
        'The maximum required value for certification is ' +
        str(MAX_AVG_LATENCY) +
        ' msec',
        metavar='KPI_LATENCY',
        type=float,
        default=1.0)
    parser.add_argument(
        '-c',
        '--fping_count',
        action='store',
        dest='fping_count',
        help='The number of fping counts to run per node and test. ' +
        'The minimum required value for certification is ' +
        str(FPING_COUNT),
        metavar='FPING_COUNT',
        type=int,
        default=500)

    parser.add_argument(
        '--no-prerequisites-check',
        action='store_false',
        dest='check_packages',
        help='To not run prerequisites checks. Those still needs to be ' +
        'installed by other means than RPM in all nodes',
        default=True)

    parser.add_argument('-v', '--version', action='version',
                        version='KOET ' + KOET_VERSION)
    args = parser.parse_args()
    if args.max_avg_latency <= 0:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "KPI latency cannot be zero or negative number\n")
    if args.fping_count <= 0:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "fping count cannot be zero or negative number\n")
    return round(args.max_avg_latency, 2), args.fping_count, args.check_packages


def check_kpi_is_ok(max_avg_latency, fping_count):
    if max_avg_latency > MAX_AVG_LATENCY:
        latency_kpi_is_good_to_certify = False
    else:
        latency_kpi_is_good_to_certify = True

    if fping_count < FPING_COUNT:
        fping_count_is_good_to_certify = False
    else:
        fping_count_is_good_to_certify = True

    return latency_kpi_is_good_to_certify,fping_count_is_good_to_certify


def show_header(koet_h_version, json_version,
                estimated_runtime_str, max_avg_latency, fping_count):
    # Say hello and give chance to disagree
    while True:
        print
        print(GREEN + "Welcome to KOET, version " + koet_h_version + NOCOLOR)
        print
        print("JSON files versions:")
        print("\tsupported OS:\t\t" + json_version['supported_OS'])
        print("\tpackages: \t\t" + json_version['packages'])
        print
        print("Please use " + GIT_URL +
              " to get latest versions and report issues about KOET.")
        print
        print(
            "The purpose of KOET is to obtain IPv4 network metrics " +
            "for a number of nodes.")
        print
        lat_kpi_ok, fping_kpi_ok = check_kpi_is_ok(max_avg_latency, fping_count)
        if lat_kpi_ok:
            print(GREEN + "The latency KPI value of " + str(max_avg_latency) +
                  " msec is good to certify the environment" + NOCOLOR)
        else:
            print(
                YELLOW +
                "WARNING: " +
                NOCOLOR +
                "The latency KPI value of " +
                str(max_avg_latency) +
                " msec is too high to certify the environment")
        print
        if fping_kpi_ok:
            print(
                GREEN +
                "The fping count value of " +
                str(fping_count) +
                " pings per test and node is good to certify the environment" +
                NOCOLOR)
        else:
            print(
                YELLOW +
                "WARNING: " +
                NOCOLOR +
                "The fping count value of " +
                str(fping_count) +
                " pings per test and node is not enough " +
                "to certify the environment")
        print
        print(
            YELLOW +
            "It requires remote ssh passwordless between all nodes for user " +
            "root already configured" +
            NOCOLOR)
        print
        print(YELLOW + "This test is going to take at least " +
              estimated_runtime_str + " minutes to complete" + NOCOLOR)
        print
        print(
            RED +
            "This software comes with absolutely no warranty of any kind. " +
            "Use it at your own risk" +
            NOCOLOR)
        print
        run_this = raw_input("Do you want to continue? (y/n): ")
        if run_this.lower() == 'y':
            break
        if run_this.lower() == 'n':
            print
            sys.exit("Have a nice day! Bye.\n")
    print


def check_os_redhat(os_dictionary):
    # Check redhat-release vs dictionary list
    redhat_distribution = platform.linux_distribution()
    redhat_distribution_str = redhat_distribution[0] + \
        " " + redhat_distribution[1]
    error_message = RED + "QUIT: " + NOCOLOR + " " + \
        redhat_distribution_str + " is not a supported OS for this tool\n"
    try:
        if os_dictionary[redhat_distribution_str] == 'OK':
            print(GREEN + "OK: " + NOCOLOR + redhat_distribution_str +
                  " is a supported OS for this tool")
            print
        else:
            sys.exit(error_message)
            print
    except Exception:
        sys.exit(error_message)
        print


def get_json_versions(os_dictionary, packages_dictionary):
    # Gets the versions of the json files into a dictionary
    json_version = {}

    # Lets see if we can load version, if not quit
    try:
        json_version['supported_OS'] = os_dictionary['json_version']
    except Exception:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "Cannot load version from supported OS JSON")
    try:
        json_version['packages'] = packages_dictionary['json_version']
    except Exception:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "Cannot load version from packages JSON")

    # If we made it this far lets return the dictionary. This was being stored
    # in its own file before
    return json_version


def check_distribution():
    # Decide if this is a redhat or a CentOS. We only checking the running
    # node, that might be a problem
    what_dist = platform.dist()[0]
    if what_dist == "redhat" or "centos":
        return what_dist
    else:  # everything esle we fail
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "this only runs on RedHat at this moment")


def ssh_rpm_is_installed(host, rpm_package):
    # returns the RC of rpm -q rpm_package or quits if it cannot run rpm
    errors = 0
    try:
        return_code = subprocess.call(['ssh',
                                       '-o',
                                       'StrictHostKeyChecking=no',
                                       host,
                                       'rpm',
                                       '-q',
                                       rpm_package],
                                      stdout=DEVNULL,
                                      stderr=DEVNULL)
    except Exception:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "cannot run rpm over ssh on host " + host)
    return return_code


def host_packages_check(hosts_dictionary, packages_dictionary):
    # Checks if packages from JSON are installed or not based on the input
    # data ont eh JSON
    errors = 0
    print("Checking packages install status:")
    print
    for host in hosts_dictionary.keys():
        for rpm_package in packages_dictionary.keys():
            if rpm_package != "json_version":
                current_package_rc = ssh_rpm_is_installed(host, rpm_package)
                expected_package_rc = packages_dictionary[rpm_package]
                if current_package_rc == expected_package_rc:
                    print(
                        GREEN +
                        "OK: " +
                        NOCOLOR +
                        "on host " +
                        host +
                        " the " +
                        rpm_package +
                        " installation status is as expected")
                else:
                    print(
                        RED +
                        "ERROR: " +
                        NOCOLOR +
                        "on host " +
                        host +
                        " the " +
                        rpm_package +
                        " installation status is *NOT* as expected")
                    errors = errors + 1
    if errors > 0:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "Fix the packages before running this tool again.\n")


def is_IP_address(ip):
    # Lets check is a full ip by counting dots
    if ip.count('.') != 3:
        return False
    try:
        socket.inet_aton(ip)
        return True
    except Exception:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "cannot check IP address " + ip + "\n")


def check_hosts_are_ips(hosts_dictionary):
    for host in hosts_dictionary.keys():
        is_IP = is_IP_address(host)
        if not is_IP:
            sys.exit(
                RED +
                "QUIT: " +
                NOCOLOR +
                "on hosts JSON file '" +
                host +
                "' is not a valid IPv4. Fix before running this tool again.\n")


def check_hosts_number(hosts_dictionary):
    number_unique_hosts = len(hosts_dictionary)
    number_unique_hosts_str = str(number_unique_hosts)
    if len(hosts_dictionary) > 32 or len(hosts_dictionary) < 4:
        sys.exit(
            RED +
            "QUIT: " +
            NOCOLOR +
            "the number of hosts is not valid. It is " +
            number_unique_hosts_str +
            " and should be between 4 and 32 unique hosts.\n")


def create_log_dir():
    # datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    logdir = os.path.join(
        os.getcwd(),
        'log',
        datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    try:
        os.makedirs(logdir)
        return logdir
    except Exception:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "cannot create directory " + logdir + "\n")


def latency_test(hosts_dictionary, logdir, fping_count):
    fping_count_str = str(fping_count)
    # 1:1 for all nodes
    for srchost in hosts_dictionary.keys():
        print
        print("Starting ping run from " + srchost + " to each node")
        for dsthost in hosts_dictionary.keys():
            if srchost is not dsthost:
                print("\tStarting ping from " + srchost + " to " + dsthost)
                fileurl = os.path.join(logdir, srchost + "_" + dsthost)
                command = "ssh -o StrictHostKeyChecking=no " + srchost + \
                    " fping -C " + fping_count_str + " -q -A " + dsthost
                with open(fileurl, 'wb', 0) as logfping:
                    runfping = subprocess.Popen(shlex.split(
                        command), stderr=subprocess.STDOUT, stdout=logfping)
                    runfping.wait()
                    logfping.close()
                print("\tPing from " + srchost +
                      " to " + dsthost + " completed")
        print("Ping run from " + srchost + " to each node completed")

    hosts_fping = ""
    for host in hosts_dictionary.keys():  # we ping ourselvels as well
        hosts_fping = hosts_fping + host + " "

    for srchost in hosts_dictionary.keys():
        print
        print("Starting ping run from " + srchost + " to all nodes")
        fileurl = os.path.join(logdir, srchost + "_" + "all")
        command = "ssh -o StrictHostKeyChecking=no " + srchost + \
            " fping -C " + fping_count_str + " -q -A " + hosts_fping
        with open(fileurl, 'wb', 0) as logfping:
            runfping = subprocess.Popen(shlex.split(
                command), stderr=subprocess.STDOUT, stdout=logfping)
            runfping.wait()
            logfping.close()
        print("Ping run from " + srchost + " to all nodes completed")


def mean_list(list):
    if len(list) == 0:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "cannot calculate mean of list: " + repr(list) + "\n")
    # We replace a timeout "-" for 1 sec latency
    list = [lat.replace('-', '1000.00') for lat in list]
    list = [float(lat) for lat in list]  # we convert them to float
    mean = sum(list) / len(list)
    return mean


def max_list(list):
    if len(list) == 0:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "cannot calculate max of list: " + repr(list) + "\n")
    # We replace a timeout "-" for 1 sec latency
    list = [lat.replace('-', '1000.00') for lat in list]
    list = [float(lat) for lat in list]
    max_lat = max(list)
    return max_lat


def min_list(list):
    if len(list) == 0:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "cannot calculate min of list: " + repr(list) + "\n")
    # We replace a timeout "-" for 1 sec latency
    list = [lat.replace('-', '1000.00') for lat in list]
    list = [float(lat) for lat in list]
    min_lat = min(list)
    return min_lat


def stddev_list(list, mean):
    if len(list) == 0:
        sys.exit(
            RED +
            "QUIT: " +
            NOCOLOR +
            "cannot calculate standard deviation of list: " +
            repr(list) +
            "\n")
    # We replace a timeout "-" for 1 sec latency
    list = [lat.replace('-', '1000.00') for lat in list]
    list = [float(lat) for lat in list]
    stddev_lat = sqrt(float(
        reduce(lambda x, y: x + y, map(
            lambda x: (x - mean) ** 2, list))) / len(list))
    stddev_lat = Decimal(stddev_lat)
    stddev_lat = round(stddev_lat, 2)
    return stddev_lat


def load_multiple_fping(logdir, hosts_dictionary):
    all_fping_dictionary = {}
    all_fping_dictionary_max = {}
    all_fping_dictionary_min = {}
    all_fping_dictionary_stddev = {}
    mean_all = []
    max_all = []
    min_all = []
    # Loads log file and returns dictionary
    for srchost in hosts_dictionary.keys():
        print
        print("Loading ping results of " + srchost + " to all nodes")
        fileurl = os.path.join(logdir, srchost + "_all")
        logfping = open(fileurl, 'r', 0)
        for rawfping in logfping:
            hostIP = rawfping.split(':')[0]
            hostIP = hostIP.rstrip(' ')
            if srchost == hostIP:  # we ignore ourselves
                continue
            latencies = rawfping.split(':')[1]
            latencies = latencies.lstrip(' ')  # Clean up first space
            latencies = latencies.rstrip('\n')  # Clean up new line character
            latencies_list = latencies.split(' ')
            # our mean calculation expect strings. Need to change this when
            # optimizing
            mean_all.append(str(mean_list(latencies_list)))
            max_all.append(max(latencies_list))
            min_all.append(min(latencies_list))
        # we use Decimal to round the results
        mean = Decimal(mean_list(mean_all))
        mean = round(mean, 2)  # we round to 2 decimals
        all_fping_dictionary[srchost] = mean
        all_fping_dictionary_max[srchost] = max_list(max_all)
        all_fping_dictionary_min[srchost] = min_list(min_all)
        all_fping_dictionary_stddev[srchost] = stddev_list(mean_all, mean)
        print("Load ping results from " + srchost + " to all nodes completed")
    return (all_fping_dictionary, all_fping_dictionary_max,
            all_fping_dictionary_min, all_fping_dictionary_stddev)


def load_single_fping(logdir, hosts_dictionary):
    single_fping_dictionary = {}
    single_fping_dictionary_max = {}
    single_fping_dictionary_min = {}
    single_fping_dictionary_stddev = {}
    # Loads log file and return dictinary
    for srchost in hosts_dictionary.keys():
        print
        print("Loading ping results of " + srchost + " to each node")
        for dsthost in hosts_dictionary.keys():
            if srchost is not dsthost:
                print("\tLoading from " + srchost + " to " + dsthost)
                fileurl = os.path.join(logdir, srchost + "_" + dsthost)
                try:
                    with open(fileurl, 'r', 0) as logfping:
                        rawfping = logfping.readline()  # Only 1 line
                        hostIP = rawfping.split(':')[0]
                        hostIP = hostIP.rstrip(' ')
                        latencies = rawfping.split(':')[1]
                        latencies = latencies.lstrip(
                            ' ')  # Clean up first space
                        # Clean up new line character
                        latencies = latencies.rstrip('\n')
                        latencies_list = latencies.split(' ')
                        print("\tLoaded from " + srchost +
                              " to " + dsthost + " completed")
                except Exception:
                    sys.exit(RED + "QUIT: " + NOCOLOR +
                             "Cannot parse LOG file: " + fileurl)
                # Following calls need to be optimized
                # we use Decimal to round the results
                mean = Decimal(mean_list(latencies_list))
                mean = round(mean, 2)  # we round to 2 decimals
                single_fping_dictionary[hostIP] = mean
                single_fping_dictionary_max[hostIP] = max_list(latencies_list)
                single_fping_dictionary_min[hostIP] = min_list(latencies_list)
                single_fping_dictionary_stddev[hostIP] = stddev_list(
                    latencies_list, mean)
        print("Load ping results from " + srchost + " to each node completed")
    return (single_fping_dictionary, single_fping_dictionary_max,
            single_fping_dictionary_min, single_fping_dictionary_stddev)


def fping_KPI(
        fping_dictionary,
        fping_dictionary_max,
        fping_dictionary_min,
        fping_dictionary_stddev,
        test_string,
        max_avg_latency,
        max_max_latency,
        max_stddev_latency):
    errors = 0
    print("Results for test " + test_string + "")
    max_avg_latency_str = str(round(max_avg_latency, 2))
    max_max_latency_str = str(round(max_max_latency, 2))
    max_stddev_latency_str = str(round(max_stddev_latency, 2))
    for host in fping_dictionary.keys():
        if fping_dictionary[host] >= max_avg_latency:
            errors = errors + 1  # yes yes +=
            print(RED +
                  "ERROR: " +
                  NOCOLOR +
                  "on host " +
                  host +
                  " the " +
                  test_string +
                  " average latency is " +
                  str(fping_dictionary[host]) +
                  " msec. Which is higher than the KPI of " +
                  max_avg_latency_str +
                  " msec")
        else:
            print(GREEN +
                  "OK: " +
                  NOCOLOR +
                  "on host " +
                  host +
                  " the " +
                  test_string +
                  " average latency is " +
                  str(fping_dictionary[host]) +
                  " msec. Which is lower than the KPI of " +
                  max_avg_latency_str +
                  " msec")

        if fping_dictionary_max[host] >= max_max_latency:
            errors = errors + 1
            print(RED +
                  "ERROR: " +
                  NOCOLOR +
                  "on host " +
                  host +
                  " the " +
                  test_string +
                  " maximum latency is " +
                  str(fping_dictionary_max[host]) +
                  " msec. Which is higher than the KPI of " +
                  max_max_latency_str +
                  " msec")
        else:
            print(GREEN +
                  "OK: " +
                  NOCOLOR +
                  "on host " +
                  host +
                  " the " +
                  test_string +
                  " maximum latency is " +
                  str(fping_dictionary_max[host]) +
                  " msec. Which is lower than the KPI of " +
                  max_max_latency_str +
                  " msec")

        if fping_dictionary_min[host] >= max_avg_latency:
            errors = errors + 1
            print(RED +
                  "ERROR: " +
                  NOCOLOR +
                  "on host " +
                  host +
                  " the " +
                  test_string +
                  " minimum latency is " +
                  str(fping_dictionary_min[host]) +
                  " msec. Which is higher than the KPI of " +
                  max_avg_latency_str +
                  " msec")
        else:
            print(GREEN +
                  "OK: " +
                  NOCOLOR +
                  "on host " +
                  host +
                  " the " +
                  test_string +
                  " minimum latency is " +
                  str(fping_dictionary_min[host]) +
                  " msec. Which is lower than the KPI of " +
                  max_avg_latency_str +
                  " msec")

        if fping_dictionary_stddev[host] >= max_stddev_latency:
            errors = errors + 1
            print(RED +
                  "ERROR: " +
                  NOCOLOR +
                  "on host " +
                  host +
                  " the " +
                  test_string +
                  " standard deviation of latency is " +
                  str(fping_dictionary_stddev[host]) +
                  " msec. Which is higher than the KPI of " +
                  max_stddev_latency_str +
                  " msec")
        else:
            print(GREEN +
                  "OK: " +
                  NOCOLOR +
                  "on host " +
                  host +
                  " the " +
                  test_string +
                  " standard deviation of latency is " +
                  str(fping_dictionary_stddev[host]) +
                  " msec. Which is lower than the KPI of " +
                  max_stddev_latency_str +
                  " msec")
        print

    return errors  # Use this to give number of nods is not exact in all cases


def test_ssh(hosts_dictionary):
    for host in hosts_dictionary.keys():
        try:
            ssh_return_code = subprocess.call(['ssh',
                                               '-oStrictHostKeyChecking=no',
                                               '-oBatchMode=yes',
                                               host,
                                               'uname'],
                                              stdout=DEVNULL,
                                              stderr=DEVNULL)
            if ssh_return_code == 0:
                print(GREEN + "OK: " + NOCOLOR +
                      "SSH with node " + host + " works")
            else:
                sys.exit(
                    RED +
                    "QUIT: " +
                    NOCOLOR +
                    "cannot run ssh to " +
                    host +
                    ". Please fix this problem before running this tool again")
        except Exception:
            sys.exit(
                RED +
                "QUIT: " +
                NOCOLOR +
                "cannot run ssh to " +
                host +
                ". Please fix this problem before running this tool again")
    print


def print_end_summary(s_avg_fp_err, a_avg_fp_err, lat_kpi_ok, fping_kpi_ok):
    # End summary and say goodbye
    passed = True
    print
    print("The summary of this run:")
    print

    if s_avg_fp_err > 0:
        print(RED + "\tThe 1:1 fping latency test failed " +
              str(s_avg_fp_err) + " time[s]" + NOCOLOR)
        passed = False
    else:
        print(
            GREEN +
            "\tThe 1:1 fping latency was successful in all nodes" +
            NOCOLOR)

    if a_avg_fp_err > 0:
        print(RED + "\tThe 1:n fping  latency test failed " +
              str(a_avg_fp_err) + " time[s]" + NOCOLOR)
        passed = False
    else:
        print(
            GREEN +
            "\tThe 1:n fping average latency was successful in all nodes" +
            NOCOLOR)
    print

    if passed:
        print (
            GREEN +
            "OK: " +
            NOCOLOR +
            "All tests had been passed" +
            NOCOLOR)
    else:
        print(
            RED +
            "ERROR: " +
            NOCOLOR +
            "All test must be passed to certify the environment " +
            "to proceed with the next steps" +
            NOCOLOR)

    if lat_kpi_ok and fping_kpi_ok and passed:
        print (
            GREEN +
            "OK: " +
            NOCOLOR +
            "You can proceed with the next steps" +
            NOCOLOR)
        valid_test = 0
    else:
        print(
            RED +
            "ERROR: " +
            NOCOLOR +
            "This run is not valid to certify the environment. " +
            "You cannot proceed with the next steps" +
            NOCOLOR)
        valid_test = 5
    print
    return (s_avg_fp_err + a_avg_fp_err + valid_test)

def main():
    # Parsing input
    max_avg_latency, fping_count, check_packages = parse_arguments()
    max_max_latency = max_avg_latency * 2
    max_stddev_latency = max_avg_latency / 3

    # JSON loads
    os_dictionary = load_json("supported_OS.json")
    packages_dictionary = load_json("packages.json")
    hosts_dictionary = load_json("hosts.json")

    # Check hosts are IP addresses
    check_hosts_are_ips(hosts_dictionary)

    # Check hosts are 4 to 32
    check_hosts_number(hosts_dictionary)

    # Initial header
    json_version = get_json_versions(os_dictionary, packages_dictionary)
    estimated_runtime_str = str(
        estimate_runtime(hosts_dictionary, fping_count))
    show_header(KOET_VERSION, json_version, estimated_runtime_str,
                max_avg_latency, fping_count)

    # Checks
    # Check OS
    linux_distribution = check_distribution()

    if linux_distribution == "redhat" or "centos":
        check_os_redhat(os_dictionary)
    else:
        sys.exit(RED + "QUIT: " + NOCOLOR +
                 "cannot determine Linux distribution\n")

    # Check SSH
    test_ssh(hosts_dictionary)

    # Check packages are installed
    if check_packages:
        host_packages_check(hosts_dictionary, packages_dictionary)
    else:
        print(YELLOW + "WARNING: " + NOCOLOR + "prerequisites not checked." +
        " Please ensure than the tools required are installed in all nodes")

    # Run
    logdir = create_log_dir()
    latency_test(hosts_dictionary, logdir, fping_count)

    # Load results
    single_fping_dictionary, single_fping_dictionary_max, \
        single_fping_dictionary_min, single_fping_dictionary_stddev = \
        load_single_fping(logdir,
                          hosts_dictionary)
    all_fping_dictionary, all_fping_dictionary_max, all_fping_dictionary_min, \
        all_fping_dictionary_stddev = load_multiple_fping(logdir,
                                                          hosts_dictionary)

    # Compare againsts KPIs
    print
    single_avg_fping_errors = fping_KPI(
        single_fping_dictionary,
        single_fping_dictionary_max,
        single_fping_dictionary_min,
        single_fping_dictionary_stddev,
        "1:1",
        max_avg_latency,
        max_max_latency,
        max_stddev_latency)
    all_avg_fping_errors = fping_KPI(
        all_fping_dictionary,
        all_fping_dictionary_max,
        all_fping_dictionary_min,
        all_fping_dictionary_stddev,
        "1:n",
        max_avg_latency,
        max_max_latency,
        max_stddev_latency)

    # Exit protocol
    lat_kpi_ok, fping_kpi_ok = check_kpi_is_ok(max_avg_latency, fping_count)
    DEVNULL.close()
    return_code = print_end_summary(
        single_avg_fping_errors,
        all_avg_fping_errors,
        lat_kpi_ok,
        fping_kpi_ok)
    print
    return return_code


if __name__ == '__main__':
    main()
