#!/bin/sh

echo ::debug::ARGS=\("$1", "$2", "$3", "$4", "$5"\)

/query_issues.py -t "$1" -r "$2" -a "$3" -s "$4" -f "$5"
