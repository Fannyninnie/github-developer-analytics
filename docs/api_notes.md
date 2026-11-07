# API exploration notes

## Fields I plan to keep

| Entity | Fields |
|---|---|
| Repository | id, full_name, language, created_at, pushed_at, stargazers_count, forks_count, open_issues_count |
| Commit | sha, repo, author login, author name, committed date, message |
| Issue | id, number, repo, state, created_at, closed_at, author login, comments |
| Pull request | id, number, repo, state, created_at, closed_at, merged_at, author login |

## Gotchas I found
- The issues endpoint also returns pull requests.
- Commit author login can be null.
- Everything is paginated (max 100 per page).
- Flask has about 5,500 commits, so the first load needs a date limit.