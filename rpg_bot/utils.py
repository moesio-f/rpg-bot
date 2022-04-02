import argparse
import typing

from rpg_bot.cogs.music.ost_key import OSTKey


owner_ids = [300222466788425728, 419533052222373908,
             335193595911077899, 952627911586877460]


class ClientInput(typing.NamedTuple):
  token: str
  urls: typing.List[str]


def parse_arguments() -> ClientInput:
  parser = argparse.ArgumentParser(description='A simple discord bot.')
  parser.add_argument('-f', type=str, required=True,
                      dest='url_filename')
  parser.add_argument('-t', type=str, required=True,
                      dest='bot_token')
  args = parser.parse_args()
  token: str = args.bot_token
  url_fname = args.url_filename

  if token.endswith(".txt"):
    with open(token) as file:
      token = file.readline()

  return ClientInput(token=token,
                     urls=read_urls(url_fname))


def read_urls(fname: str) -> typing.Dict[OSTKey, typing.List[str]]:
  dictionary = {k: [] for k in OSTKey}
  with open(fname, 'r') as file:
    for line in file:
      splitted = line.split(":", 1)
      key = OSTKey.from_str(splitted[0][0])
      url = splitted[1]
      dictionary[key].append(url)

  return dictionary


def check_is_owner(ctx):
  return ctx.message.author.id in owner_ids


def is_spotify_track(url):
  return "open.spotify.com" in url and "track" in url
