# Crowdin-Top-Contributor-Listing
 Python script automatically find top contributors for Snap Hutao project

## Required Environment Variables

- `TOKEN`: Crowdin API token -> `str`
  - Require scopes **Projects (List, Get, Create, Edit)**, **Report**, **Source file & strings** privileges
- `PROJECT_ID`: Crowdin project ID -> `int`
- `BRANCH_NAME`: Crowdin branch name -> `str`
- `PROJECT_START_YEAR`: Crowdin project start year -> `int`
- `PROJECT_START_MONTH`: Crowdin project start month -> `int`
- `PROJECT_START_DAY`: Crowdin project start day -> `int`
- `IGNORED_MEMBERS`: Crowdin usernames to ignore, used to avoid project owner/manager-> `str` (comma separated)
- `REWARD_MESSAGE`: Message to send to top contributors -> `str`
  - Use `{user_full_name}` as template for rewarded user's full name
  - Use `{reward}` as template for reward amount
  - Use `{license_key}` as template for license key
- `MYSQL_HOST`: MySQL host -> `str`
- `MYSQL_PORT`: MySQL port -> `int`
- `MYSQL_USER`: MySQL user -> `str`
- `MYSQL_PASSWORD`: MySQL password -> `str`
- `MYSQL_DATABASE`: MySQL database -> `str`
- `CODE_SYSTEM_KEY`: Code system API token key -> `str`