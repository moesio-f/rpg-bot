import typing

from spotdl.search import spotify_client
from discord.ext import commands

from rpg_bot.cogs import music


def start_bot(urls: typing.Dict[music.ost_key.OSTKey, typing.List[str]],
              token: str):
    bot = commands.Bot(command_prefix='$$')

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('------')

    spotify_client.SpotifyClient.init(
        client_id="5f573c9620494bae87890c0f08a60293",
        client_secret="212476d9b0f3472eaa762d90b19b0ba8",
        user_auth=False)

    bot.add_cog(music.soundtrack.Soundtrack(bot=bot, urls=urls))
    bot.run(token)
