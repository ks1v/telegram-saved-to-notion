# Telegram Saved Messages to a Notion Database

Import Telegram Saved messages into a Notion database. It creates separate pages for each day and writes messages as time-tagged blocks. Start of each day is not a midnight but actual time when you slept according to a gaps in messages flow.

## TODO
- [x] Python binding with Telegram
- [x] Load Saved messages as a JSON file
- [x] Process Saved messages into a DataFrame (retain essencial fields, download and link media)
- [x] Split Saved messages by adjusted dates according to night gap in messages flow
- [ ] Python binding with Notion
- [ ] Connect to test Notion database
- [ ] Create daily pages with messages in time-tagged blocks
- [ ] Convert links to web bookmarks
- [ ] Attach media files to pages

## Dependences:

1. [Telethon](https://github.com/LonamiWebs/Telethon)
1. [Pandas](https://github.com/pandas-dev/pandas)

	> pip install telethon pandas







