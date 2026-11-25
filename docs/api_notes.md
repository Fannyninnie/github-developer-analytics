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
- `open_issues_count` on a repo includes open pull requests, so it is not the same as the number of open issues.
- Repo stars and forks are only available as a current total, so a snapshot must be saved every day to keep history.
- The pulls endpoint has no `since` filter, so incremental extraction sorts by `updated_at` descending and stops at the bookmark.
- `since` on issues filters by `updated_at`, so the same issue can appear in several extracts and staging must keep the latest version.


## How incremental commit extraction works
(2 to 3 sentences: what happens on the first run, what the bookmark file stores, and what happens on the next run)

- The pulls endpoint has no `since` filter, so incremental extraction sorts by `updated_at` descending and stops at the bookmark.
- `since` on issues filters by `updated_at`, so the same issue can appear in several extracts and staging must keep the latest version.

- GitHub's `since` filter on commits uses the committer date. Author dates can be much older, so activity charts should use `commit.committer.date`.

- GitHub repos get renamed. `dbt-labs/dbt-core` is now `dbt-labs/dbt`, and the old name redirects. The API reports the current name, so the loader maps names from `repos.txt` to the canonical name. A foreign-key check between facts and `dim_repo` found it.

- Some automation accounts do not end in `[bot]` (for example `fa-assistant`, which does dbt release chores). `dim_contributor.is_automation` holds a short, manually judged list. In production this would be a maintained seed file.
- Snapshot dates are in UTC, so an evening run in Los Angeles can be stamped with the next day's date.
