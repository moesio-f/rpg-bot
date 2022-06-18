import typing
import collections
import random

from discord.ext import commands
from spotdl.search import song_gatherer

from rpg_bot.cogs.music import utils
from rpg_bot.cogs.music import track_source, track_info, ost_key


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

        def update_url(track):
            if utils.is_spotify_track(track.url):
                track.url = song_gatherer.from_spotify_url(
                    spotify_url=track.url).youtube_link

        self._update_url_if_spotify = update_url
        self._bot.loop.run_until_complete(self.__initialize())

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
            return await ctx.send(f'{t} não é um tipo de OST válido.')

        track = track_info.TrackInfo(url=url)
        self._update_url_if_spotify(track)
        data = await track_source.TrackSource.fetch_data(track.url,
                                                         loop=self._bot.loop,
                                                         download=False)
        track.title = data.get('title')
        track.duration = utils.format_duration(data.get('duration'))
        self._tracks[key].append(track)
        await ctx.send(f'Faixa \"{track.title}\" ({track.duration}) adicionada.')

    @commands.command(aliases=['r', 'rem'])
    async def remove(self, ctx, value: str):
        """
        Remove a music track from the current track list and update IDs.

        :param value: track identifier ({OST Type}{ID})
        """
        key = ost_key.OSTKey.from_str(value[0])
        index = int(value[1:]) - 1

        if key is None or index not in range(len(self._tracks[key])):
            return await ctx.send(f'Faixa inválida.')

        title = self._tracks[key][index].title
        del self._tracks[key][index]
        await ctx.send(f'Faixa \"{title}\" ({key.name}{index + 1}) removida.')

    @commands.command(aliases=['p'])
    async def play(self, ctx, value: str):
        """
        Plays a music track in loop.

        :param value: track identifier ({OST Type}{ID})
        """
        key = ost_key.OSTKey.from_str(value[0])
        index = int(value[1:]) - 1

        if key is None or index not in range(len(self._tracks[key])):
            return await ctx.send(f'Faixa inválida.')
        else:
            self._current_track = ost_key.KeyIndex(key=key, index=index)

        track = await track_source.TrackSource.from_url(
            self._tracks[key][index].url,
            loop=self._bot.loop,
            stream=True)

        async with ctx.typing():
            ctx.voice_client.play(track,
                                  after=lambda e: print(e) if e else None)

        track_info = self._current_track
        await ctx.send('Tocando '
                       f'{key.name}{index + 1}: '
                       f'\"{track_info.title}\" ({track_info.duration})'
                       'na caixa!!')

    @commands.command(aliases=['g', 'group'])
    async def play_group(self, ctx, value: str):
        """
        Plays random music tracks of a given OST type in loop.

        :param value: OST type
        """
        key = ost_key.OSTKey.from_str(value[0])

        if key is None:
            return await ctx.send(f'Grupo inválido.')
        else:
            k = self._current_track.key
            index = self._current_track.index
            index_pool = list(range(len(self._tracks[key])))

            if k == key:
                del index_pool[index]

            index = random.choice(index_pool)
            self._current_track = ost_key.KeyIndex(key=key, index=index)

        track = await track_source.TrackSource.from_url(
            self._tracks[key][index].url,
            loop=self._bot.loop,
            stream=True,
            loop_stream=False)

        def _play_next(error):
            if error:
                print(error)
            else:
                self._bot.loop.create_task(self.play_group(ctx, value))

        async with ctx.typing():
            ctx.voice_client.play(track, after=_play_next)

        await ctx.send('Tocando '
                       f'{key.name}{index + 1}: '
                       f'\"{self._tracks[key][index].title}\" '
                       'na caixa!!')

    @commands.command(aliases=['v', 'vol'])
    async def volume(self, ctx, volume: int):
        """
        Controls the music volume.

        :param volume: integer 
        """
        if ctx.voice_client is None:
            return await ctx.send("Você não está conectado a um canal de voz.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Volume alterado para {volume}%")

    @commands.command(aliases=['s'])
    async def stop(self, ctx):
        """
        Stop playing the current track and leave channel.
        """
        await self.clear(ctx)
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send('Saindo do canal.')

    @commands.command(aliases=['c'])
    async def clear(self, ctx):
        """
        Stop playing the current track.
        """
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send('Parando de tocar.')

    @commands.command()
    async def current(self, ctx):
        """
        Prints information of the current playing track.
        """
        if ctx.voice_client and ctx.voice_client.is_playing():
            k = self._current_track.key
            i = self._current_track.index
            current_track = self._tracks[k][i]
            await ctx.send(f"\"{current_track.title}\" "
                           f"(Faixa {k.name}{i + 1}, {current_track.duration}) "
                           "está atualmente tocando.")
        else:
            await ctx.send("Nenhuma faixa tocando no momento.")

    @commands.command(aliases=['l'])
    async def list(self, ctx):
        """
        List all music tracks.
        """
        ordered_dict = collections.OrderedDict(sorted(self._tracks.items(),
                                                      key=lambda k: str(k[0].name)))
        music_list = [f"{k.name}{i + 1}:\t{t.title} ({t.duration})"
                      for k, l in ordered_dict.items()
                      for i, t in enumerate(l)]
        await ctx.send('Músicas na lista:')

        entries = 10

        async with ctx.typing():
            for i in range(0, len(music_list), entries):
                music_str = '\n'.join(music_list[i:i+entries])
                await ctx.send(f"```{music_str}```")

    @play.before_invoke
    @play_group.before_invoke
    async def ensure_voice(self, ctx):
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
