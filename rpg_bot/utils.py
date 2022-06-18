"""
Utility methods and classes for the program's entry point.
"""

import argparse
import typing

from rpg_bot.cogs.music.ost_key import OSTKey


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
