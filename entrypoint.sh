#!/bin/sh -l

echo ::set-output name=debug::ARGS: \("$1", "$2", "$3", "$4"\)

/query_issues.py -t "$1" -r "$2" -a "$3" -s "$4"
