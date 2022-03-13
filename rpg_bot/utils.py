import argparse
import typing


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


def read_urls(fname: str) -> typing.List[str]:
  urls = []
  with open(fname, 'r') as file:
    for line in file:
      urls.append(line)
  return urls


def check_is_owner(ctx):
  return ctx.message.author.id == 300222466788425728


def is_spotify_track(url):
  return "open.spotify.com" in url and "track" in url
