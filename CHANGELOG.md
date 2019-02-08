Changelog:


- 1.0:
    - Initial release. Includes average calculation of ICMP replies 1:1 and 1:n

- 1.1:
    - number of pings per test and KPI latency can be passed as optional argument
    - small fixes

- 1.2:
    - In addition to average now we check and show max response time against KPIs
    - small fixes on error messages

- 1.3
    - In addition to max and average we check and show min response time against KPIs
    - In addition to max and average we check and show standard deviation time against KPIs
    - small fixes on messages

- 1.4
    - Calculate different KPI for max and standard deviation
    - Some sanity check on the input
    - small fixes on messages

- 1.5
    - Check number of unique nodes are at least 4 and no more than 32
    - Fix 1:n summary error count

- 1.6
    - PEP8 formatting
    - small fixes on messages

- 1.7
    -Fixed #1 "Add warning on final summary if run is less than KPI requirements"

- TODO:
    - Code optimizations
    - Code clean up
    - Load already run tests
