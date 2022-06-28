# RPG Bot 🤖

A simple Discord bot using Python for managing online tabletop RPG activities and tasks.

## Features

- Soundtrack Manager: manages different tracks by groups, enabling to play ambient music for specific situations.

## Dependencies/Requirements

- [FFmpeg](https://ffmpeg.org/): _A complete, cross-platform solution to record, convert and stream audio and video._
- Python 3.6+
- [discord.py](https://github.com/Rapptz/discord.py): _An API wrapper for Discord written in Python._
- Other requirements listed in `requirements.txt`

To install the Python dependencies (including `discord.py`) simply run in a [virtual environment](https://docs.python.org/3/library/venv.html) (preferably):`
```sh
python -m pip install -r requirements.txt`
```

FFmpeg instalation is system-dependent.

## Usage

The script `discord_bot_main.py` provides a simple CLI to start and interact with the bot. It requires two arguments:

1. A file containg a list of initial soundtracks.
2. A discord bot token (or file containing the token).

Then, the bot can be started by running:

```sh
python discord_bot_main.py -f <FILE> -t <TOKEN>
``` 
