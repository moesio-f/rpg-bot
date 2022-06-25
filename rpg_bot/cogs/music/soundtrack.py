import os
import re
import typing
import random
import asyncio
import datetime

import discord
from discord.ext import commands, tasks
from spotdl.search import song_gatherer

from rpg_bot.cogs.music import utils
from rpg_bot.cogs.music import track_source, track_info, ost_key
from rpg_bot.cogs.music import track_list_embed


class Soundtrack(commands.Cog,
                 name='Soundtrack Manager',
                 description='A simple soundtrack manager for RPG music tracks.'):
    """
    Soundtrack manager for RPG music tracks.
    """

    def __init__(self, bot, urls: typing.Dict[ost_key.OSTKey, typing.List[str]]):
        self._bot = bot
        self._tracks = {k: [track_info.TrackInfo(url=u) for u in lu]
                        for k, lu in urls.items()}
        self._current_track: ost_key.KeyIndex = ost_key.KeyIndex(
            key=None, index=-1)
        self._tracks_info_initialized = False
        self._playing_group = False
        self._playing_group_ctx = None
        self._semaphore = asyncio.Semaphore(1)

        def update_url(track):
            if utils.is_spotify_track(track.url):
                track.url = song_gatherer.from_spotify_url(
                    spotify_url=track.url).youtube_link

        self._update_url_if_spotify = update_url
        self._bot.loop.run_until_complete(self.__initialize())
        self._group_loop.start()
        self._save_tracks()

    async def __initialize(self):
        if not self._tracks_info_initialized:
            for k in ost_key.OSTKey:
                for track in self._tracks[k]:
                    self._update_url_if_spotify(track)
                    data = await track_source.TrackSource.fetch_data(track.url,
                                                                     loop=self._bot.loop,
                                                                     download=False)
                    track.title = data.get('title')
                    track.duration = utils.format_duration(
                        data.get('duration'))
            self._tracks_info_initialized = True

    async def cog_before_invoke(self, ctx):
        await self.__initialize()

    @commands.command(aliases=['a'])
    async def add(self, ctx, t: str, url: str):
        """
        Adds a new music track to the current track list.

        :param t: OST type.
        :param url: music track URL.
        """
        key = ost_key.OSTKey.from_str(t)

        if key is None:
            e = discord.Embed(title="",
                              description=f'{t} não é um tipo de OST válido.',
                              color=discord.Color.dark_red())
            return await ctx.send(content='', embed=e)

        track = track_info.TrackInfo(url=url)
        self._update_url_if_spotify(track)
        data = await track_source.TrackSource.fetch_data(track.url,
                                                         loop=self._bot.loop,
                                                         download=False)
        track.title = data.get('title')
        track.duration = utils.format_duration(data.get('duration'))
        self._tracks[key].append(track)

        e = discord.Embed(title="",
                          description=f'Faixa \"{track.title}\" ({track.duration}) adicionada.',
                          color=discord.Color.dark_green())
        await ctx.send(content='', embed=e)
        await ctx.message.delete()

    @commands.command(aliases=['r', 'rem'])
    async def remove(self, ctx, value: str):
        """
        Remove a music track from the current track list and update IDs.

        :param value: track identifier ({OST Type}{ID})
        """
        key = ost_key.OSTKey.from_str(value[0])
        index = int(value[1:]) - 1

        if key is None or index not in range(len(self._tracks[key])):
            e = discord.Embed(title="",
                              description="Faixa inválida.",
                              color=discord.Color.dark_red())
            return await ctx.send(content='', embed=e)

        title = self._tracks[key][index].title
        del self._tracks[key][index]
        e = discord.Embed(title="",
                          description=f'Faixa \"{title}\" ({key.name}{index + 1}) removida.',
                          color=discord.Color.dark_green())
        await ctx.send(content='', embed=e)
        await ctx.message.delete()

    @commands.command(aliases=['p'])
    async def play(self, ctx, value: str):
        """
        Plays a music track in loop.

        :param value: track identifier ({OST Type}{ID})
        """
        key = ost_key.OSTKey.from_str(value[0])
        index = int(value[1:]) - 1

        if key is None or index not in range(len(self._tracks[key])):
            e = discord.Embed(title="",
                              description="Faixa inválida.",
                              color=discord.Color.dark_red())
            return await ctx.send(content='', embed=e)

        async with self._semaphore:
            self._current_track = ost_key.KeyIndex(key=key, index=index)
            await self._play_track(ctx, key, index, stream=True, loop_stream=True)

        await ctx.message.delete()

    @commands.command(aliases=['g'])
    async def group(self, ctx, value: str):
        """
        Plays random music tracks of a given OST type in loop.

        :param value: OST type
        """
        key = ost_key.OSTKey.from_str(value)

        if key is None or not len(self._tracks[key]):
            async with self._semaphore:
                self._playing_group = False
            e = discord.Embed(title="",
                              description="Grupo inválido.",
                              color=discord.Color.dark_red())
            return await ctx.send(content='', embed=e)

        async with self._semaphore:
            # Start playing the tracks in the group
            self._playing_group = True
            self._playing_group_ctx = ctx
            await self._play_next_track_in_group(ctx, key)

        await ctx.message.delete()

    @commands.command(aliases=['v', 'vol'])
    async def volume(self, ctx, volume: int):
        """
        Controls the music volume.

        :param volume: integer
        """
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            e = discord.Embed(title="",
                              description="Nenhuma música está tocando.",
                              color=discord.Color.dark_red())
            return await ctx.send(content='', embed=e)

        ctx.voice_client.source.volume = volume / 100

        blocks = []

        for i in range(10):
            t = (i + 1) * 10
            if volume >= t:
                blocks.append("🟩")
            else:
                blocks.append("⬛")

        e = discord.Embed(title="",
                          description=f"Volume: {' '.join(blocks)} ({volume}%)",
                          color=discord.Color.dark_teal())

        await ctx.send(content="", embed=e)
        await ctx.message.delete()

    @commands.command(aliases=['s'])
    async def stop(self, ctx):
        """
        Stop playing the current track and leave channel.
        """
        await self.clear(ctx)
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            e = discord.Embed(title="",
                              description="Saindo do canal.",
                              color=discord.Color.dark_red())
            await ctx.send(content='', embed=e)
            await ctx.message.delete()

    @commands.command(aliases=['c'])
    async def clear(self, ctx):
        """
        Stop playing the current track.
        """
        async with self._semaphore:
            self._playing_group = False

            if ctx.voice_client and ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                e = discord.Embed(title="",
                                  description="Parando de tocar.",
                                  color=discord.Color.dark_red())
                await ctx.send(content='', embed=e)
                await ctx.message.delete()

    @commands.command()
    async def current(self, ctx):
        """
        Prints information of the current playing track.
        """
        async with self._semaphore:
            if ctx.voice_client and ctx.voice_client.is_playing():
                k = self._current_track.key
                i = self._current_track.index
                current_track = self._tracks[k][i]

                e = discord.Embed(title="",
                                  description=f"{current_track.title}",
                                  color=discord.Color.dark_teal())
                e.add_field(name='Faixa',
                            value=f'[{k.name}{i+1}]({current_track.url})')
                e.add_field(name='Duração',
                            value=f'{current_track.duration}')
                await ctx.send(content="", embed=e)
            else:
                e = discord.Embed(title="",
                                  description="Nenhuma faixa tocando no momento.",
                                  color=discord.Color.dark_teal())
                await ctx.send(content='', embed=e)

        await ctx.message.delete()

    @commands.command(aliases=['l'])
    async def list(self, ctx):
        """
        List all music tracks.
        """

        await ctx.message.delete()

        def check(_, user):
            return user == ctx.author

        manager = track_list_embed.TrackListEmbedManager(self._tracks)
        e = manager.home()

        message = await ctx.send(content=e.content,
                                 embed=e.embed)

        if e.clear_reactions:
            await message.clear_reactions()

        for emoji in e.reactions:
            await message.add_reaction(emoji)

        while True:
            try:
                reaction, _ = await self._bot.wait_for("reaction_add", timeout=60.0, check=check)
                e = manager.react(reaction.emoji)

                if e.clear_reactions:
                    await message.clear_reactions()

                await message.edit(content=e.content,
                                   embed=e.embed)

                for emoji in e.reactions:
                    await message.add_reaction(emoji)

            except asyncio.TimeoutError:
                await message.delete()
                break

    @commands.command()
    async def save(self, ctx):
        """
        Save current OST tracks in the list.
        """
        fname = self._save_tracks()
        e = discord.Embed(title="OSTs Salvas",
                          description="",
                          color=discord.Color.dark_teal())

        t = sum([len(l) for _, l in self._tracks.items()])
        d = sum([utils.from_duration_to_seconds(t.duration)
                 for _, l in self._tracks.items()
                 for t in l])

        e.add_field(name='Total de Faixas',
                    value=f'{t}')
        e.add_field(name='Duração Total',
                    value=f'{utils.format_duration_w_hours(d)}')

        for k in ost_key.OSTKey:
            i: ost_key.OSTKeyInfo = k.value
            d = sum([utils.from_duration_to_seconds(t.duration)
                     for t in self._tracks[k]])
            d = utils.format_duration_w_hours(d)
            e.add_field(name=f'{i.name}',
                        value=f'{len(self._tracks[k])} ({d})')

        await ctx.send(content='',
                       embed=e,
                       file=discord.File(fname))

        await ctx.message.delete()

    @play.before_invoke
    @group.before_invoke
    async def ensure_voice_stop_group(self, ctx):
        """
        Guarantees that play methods can play an audio and a group is not playing.
        """
        async with self._semaphore:
            # Stop playing group
            self._playing_group = False
        await self._ensure_voice(ctx)

    @add.after_invoke
    @remove.after_invoke
    async def save_tracks(self, ctx):
        self._save_tracks()

    async def _ensure_voice(self, ctx):
        """
        Guarantees that play methods can play an audio.
        """
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("Você não está conectado a um canal de voz.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @tasks.loop(seconds=0.5)
    async def _group_loop(self):
        """
        Plays the next music track for the current group.
        """
        async with self._semaphore:
            playing_group = self._playing_group
            ctx = self._playing_group_ctx
            t = self._current_track
            voice_client = ctx.voice_client if ctx else None

            if playing_group:
                # If there's a group playing, get the context and current track
                if voice_client and not voice_client.is_playing():
                    await self._play_next_track_in_group(ctx, t.key)

    async def _play_next_track_in_group(self, ctx, key: ost_key.OSTKey):
        # Before playing next track, ensure voice.
        await self._ensure_voice(ctx)

        index = await self._random_track_index_in_group(key)

        # Update current track
        self._current_track = ost_key.KeyIndex(key=key, index=index)

        await self._play_track(ctx, key, index,
                               stream=True,
                               loop_stream=False)

    async def _random_track_index_in_group(self, group: ost_key.OSTKey):
        # Get current track information
        k = self._current_track.key
        i = self._current_track.index

        # Create pool of possible indices
        index_pool = list(range(len(self._tracks[group])))

        if k == group:
            # Remove the current playing track
            # if the current (last) playing track
            # is from the same group as the target
            del index_pool[i]

        # Choose a random new index
        new_index = random.choice(index_pool)

        return new_index

    async def _play_track(self, ctx,
                          key: ost_key.OSTKey,
                          index: int,
                          stream: bool,
                          loop_stream: bool,
                          after_track=lambda e: print(e) if e else None):
        t = self._tracks[key][index]

        track = await track_source.TrackSource.from_url(
            t.url,
            loop=self._bot.loop,
            stream=stream,
            loop_stream=loop_stream)

        async with ctx.typing():
            ctx.voice_client.play(track,
                                  after=after_track)

        e = discord.Embed(title="",
                          description=f"{t.title}",
                          color=discord.Color.dark_teal())
        e.add_field(name='Faixa',
                    value=f'[{key.name}{index+1}]({t.url})')
        e.add_field(name='Duração',
                    value=f'{t.duration}')
        await ctx.send(content="", embed=e)

    def _save_tracks(self, dir: str = 'soundtracks'):
        date = datetime.datetime.today().strftime('%d-%m-%Y')
        fname = os.path.join(dir, f'ost-{date}.txt')
        content = '\n'.join([f'{k.name}:{v.url}'
                             for k, l in self._tracks.items()
                             for v in l])
        content = re.sub(r'\n+', '\n', content)

        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(fname, 'w+') as file:
            file.write(content)

        return fname
