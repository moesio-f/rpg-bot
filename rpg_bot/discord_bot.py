import typing

from spotdl.search import spotify_client
from discord.ext import commands

from rpg_bot import cogs


def start_bot(urls: typing.List[str], token: str):
  bot = commands.Bot(command_prefix='$$')

  @bot.event
  async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

  bot.add_cog(cogs.music.music_list.MusicList(bot, urls))

  spotify_client.SpotifyClient.init(
    client_id="5f573c9620494bae87890c0f08a60293",
    client_secret="212476d9b0f3472eaa762d90b19b0ba8",
    user_auth=False)
  bot.run(token)
