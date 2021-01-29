# query-issues-action

a github action to query issues from github repo. issues will be stored in a file as a json array.

## Inputs

### `token`

**Required** github token to be used to access github API. usally just use `${{ secrets.GITHUB_TOKEN }}`.

### `repo`

**Required** repo to query issues (for example: `owner/repo_name` )

### `author`

[optional] query issues created by author, default to `''`.

### `state`

[optional] query issues that are in state, default to `'OPEN'`

### `repo`

[optional][out] a file to store the issues in json format

## Outputs

no outputs ( issues are store in the file specified by `inputs.output_json` )

## Example usage

```
uses: jrdeng/query-issues-action@v1
with:
  token: ${{ secrets.GITHUB_TOKEN }}
  repo: jrdeng/jrdeng.github.io
  author: jrdeng
  output_json: ./issues.json
```
