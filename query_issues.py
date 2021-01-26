#!/usr/bin/env python3

import signal
import requests
import json
import sys
import getopt


class Issue:
    ''' the issue structure '''
    def __init__(self, issue_data):
        self.url = issue_data['url']
        self.number = self.url.split('/')[-1]
        self.title = issue_data['title']
        self.author = issue_data['author']['login'] if issue_data['author'] else 'None'
        self.createdAt = issue_data['createdAt']
        self.body = issue_data['body']
        # labels
        self.labels = []
        labels_node = issue_data['labels']
        for edge in labels_node['edges']:
            self.labels.append(edge['node']['name'])


def usage():
    print('usage: {} OPTIONS'.format(sys.argv[0]))
    print('OPTIONS:')
    print('\t-h|--help\t\tdisplay this usage')
    print('\t-t|--token TOKEN\tgithub token')
    print('\t-r|--repo REPO\t\trepo to query issues ( owner/repo_name )')
    print('\t-a|--author AUTHOR\t[optional] query issues created by AUTHOR')
    print('\t-s|--state STATE\t[optional] query issues that are in state STATE, default to "OPEN"')
    print('\t-f|--file FILE\ta file to store the issues in json format')


def github_action_set_debug_msg(msg):
    print('::debug::{}'.format(msg))


def github_action_set_error_msg(msg):
    print('::error::{}'.format(msg))


def github_action_set_output(key, value):
    print('::set-output name={}::{}'.format(key, value))


def log_error_and_exit(msg):
    # set error message, no output file generated
    github_action_set_error_msg(msg)
    exit(2)


def post_timeout_handler():
    raise Exception("POST timeout!")


def post(url, headers, payload):
    signal.signal(signal.SIGALRM, post_timeout_handler)
    signal.alarm(20)
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            log_error_and_exit(r.json())
        #print(r.json())
        data = r.json()['data']
        if data is None:
            # should be error
            log_error_and_exit(r.json())
        return data
    except Exception as ex:
        # timeout
        log_error_and_exit(ex)


def query_issues(token, repo_owner, repo_name, issue_author = None, state = 'OPEN'):
    issue_list = json.loads('[]') # return a json array, item is class Issue(as a json object)

    url = 'https://api.github.com/graphql' # TODO: use github environment variable
    headers = {'Authorization': 'bearer ' + token}

    repo_arg = 'owner: "{}", name: "{}"'.format(repo_owner, repo_name)
    issues_arg = 'first: 100, states: {}'.format(state)
    if issue_author:
        issues_arg += ', filterBy: {{ createdBy: "{}" }}'.format(issue_author)

    # NOTE: the maximum limit of nodes is 500,000.
    # modify the query_str to query data you need
    query_str_fmt = '''
    query
    {{
      repository({}) {{
        issues({}) {{
          totalCount
          edges {{
            node {{
              url
              title
              author {{
                login
                avatarUrl
              }}
              createdAt
              body
              labels(first: 50) {{
                totalCount
                edges {{
                  node {{
                    name
                  }}
                }}
              }}
            }}
            cursor
          }}
          pageInfo {{
            endCursor
            hasNextPage
          }}
        }}
      }}
    }}
    '''

    has_next_page = True
    end_cursor = ''
    index = 1
    while has_next_page:
        if len(end_cursor) == 0:
            query_first = query_str_fmt.format(repo_arg, issues_arg)
            payload = { 'query': query_first }
        else:
            query_n = query_str_fmt.format(repo_arg, issues_arg + ', after:"{}"'.format(end_cursor))
            payload = { 'query': query_n}
        print('>>>>>> querying issues ... 100 x {}'.format(index))
        index += 1
        data = post(url, headers, payload)

        # error handling
        repository = data['repository']
        if repository is None:
            log_error_and_exit('repostory does not exist')

        # pase issues
        issues = repository['issues']
        for edge in issues['edges']:
            node = edge['node']
            issue = Issue(node)
            issue_list.append(json.loads(json.dumps(issue.__dict__, ensure_ascii=False))) # obj.__dict__ --> json string --> json object

        total_count = issues['totalCount']
        print('total_count: {}'.format(total_count))

        # parse next page
        page_info = issues['pageInfo']
        end_cursor = page_info['endCursor']
        has_next_page = page_info['hasNextPage']
        print('has_next_page: {}'.format(has_next_page))

    return issue_list


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ht:r:a:s:f:', ['help', 'token=', 'repo=', 'author=', 'state=', 'file='])
    except getopt.GetoptError as err:
        usage()
        log_error_and_exit(err)
    token = None
    owner = None
    repo = None
    author = None
    state = 'OPEN'
    output_file = None
    for o, a in opts:
        if o == '-h':
            usage()
            exit()
        elif o in ('-t', '--token'):
            token = a if a != 'undefined' else None
        elif o in ('-r', '--repo'):
            kv = a.split('/')
            if len(kv) == 2:
                owner = kv[0] if kv[0] != 'undefined' else None
                repo = kv[1] if kv[1] != 'undefined' else None
        elif o in ('-a', '--author'):
            author = a if a != '' else None
        elif o in ('-s', '--state'):
            state = a # TODO handle invalide state
        elif o in ('-f', '--file'):
            output_file = a if a != '' else None
        else:
            usage()
            assert False, 'unhandled option'
    if token is None:
        usage()
        log_error_and_exit('token must be set via -t')
    if owner is None or repo is None:
        usage()
        log_error_and_exit('owner/repo_name must be set via -r')

    github_action_set_debug_msg('query_issues({}, {}, {}, {}, {})'.format(token, owner, repo, author, state))
    results = query_issues(token, owner, repo, author, state)
    issue_json_array = json.dumps(results, ensure_ascii=False)
    github_action_set_debug_msg('issue_list={}'.format(issue_json_array))
    # store output file
    if output_file:
        with open(output_file, 'w') as out:
            out.write(issue_json_array)


if __name__ == '__main__':
    main()
    github_action_set_debug_msg('DONE')
