import logging

from rpg_bot import discord_bot
from rpg_bot import utils

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
  args = utils.parse_arguments()
  discord_bot.start_bot(args.urls, args.token)
