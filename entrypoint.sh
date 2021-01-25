#!/bin/sh -l

echo ::set-output name=debug::ARGS: \("$1", "$2", "$3", "$4"\)

# TODO GITHUB_REPOSITORY passed by docker -e
/query_issues.py -t "$1" -r "$GITHUB_REPOSITORY" -a "$3" -s "$4"
