# Telegram Saved Messages to a Notion Database

Import Telegram Saved messages into a Notion database. It creates separate pages for each day and writes messages as time-tagged blocks. Start of each day is not a midnight but actual time when you slept according to a gaps in messages flow.

## TODO
- [x] Python binding with Telegram
- [x] Load Saved messages as a JSON file
- [x] Process Saved messages into a DataFrame
- [x] Split Saved Messages by dates according night gap
- [ ] Python binding with Notion
- [ ] Connect test Notion database
- [ ] Create daily pages with messages in time-tagged blocks

- [ ] Move links to message body
- [ ] Load text-only messages into the test DB
- [ ] See how to import messages containing media files

## Dependences:

1. [Telethon](https://github.com/LonamiWebs/Telethon)

	> pip install telethon



> ex.keys()
> dict_keys(['url', 'forward', 'music', 'contact', 'location', 'file', 'image', 'video', 'sticker', 'text'])







