import typing

from discord.ext import commands
from spotdl.search import song_gatherer

from rpg_bot import utils
from rpg_bot.cogs.music import track_source, track_info


class MusicList(commands.Cog):
  def __init__(self, bot, urls: typing.List[str]):
    self._bot = bot
    self._tracks = [track_info.TrackInfo(url=u) for u in urls]
    self._current_track_idx: int = -1
    self._tracks_info_initialized = False

    def update_url(track):
      if utils.is_spotify_track(track.url):
        track.url = song_gatherer.from_spotify_url(
          spotify_url=track.url).youtube_link

    self._update_url_if_spotify = update_url

  async def cog_check(self, ctx):
    return utils.check_is_owner(ctx)

  async def cog_before_invoke(self, ctx):
    if not self._tracks_info_initialized:
      for track in self._tracks:
        self._update_url_if_spotify(track)
        data = await track_source.TrackSource.fetch_data(track.url,
                                                         loop=self._bot.loop,
                                                         download=False)
        track.title = data.get('title')
      self._tracks_info_initialized = True

  @commands.command(aliases=['a'])
  async def add(self, ctx, url: str):
    track = track_info.TrackInfo(url=url)
    self._update_url_if_spotify(track)
    data = await track_source.TrackSource.fetch_data(track.url,
                                                     loop=self._bot.loop,
                                                     download=False)
    track.title = data.get('title')
    self._tracks.append(track)
    await ctx.send(f'Faixa \"{self._tracks[-1].title}\" adicionada.')

  @commands.command(aliases=['r', 'rem'])
  async def remove(self, ctx, index: int):
    if index not in range(len(self._tracks)):
      return await ctx.send(f'Faixa inválida.')

    title = self._tracks[index].title
    del self._tracks[index]
    await ctx.send(f'Faixa {index} (\"{title}\") removida.')

  @commands.command(aliases=['p'])
  async def play(self, ctx, index: int):
    if index not in range(len(self._tracks)):
      return await ctx.send(f'Faixa inválida.')
    else:
      self._current_track_idx = index

    track = await track_source.TrackSource.from_url(
      self._tracks[index].url, loop=self._bot.loop, stream=True)

    async with ctx.typing():
      ctx.voice_client.play(track,
                            after=lambda e: print(e) if e else None)

    await ctx.send('Tocando '
                   f'\"{self._tracks[index].title}\" '
                   'na caixa!!')

  @commands.command(aliases=['v', 'vol'])
  async def volume(self, ctx, volume: int):
    if ctx.voice_client is None:
      return await ctx.send("Você não está conectado a um canal de voz.")

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Volume alterado para {volume}%")

  @commands.command(aliases=['s'])
  async def stop(self, ctx):
    await self.clear(ctx)
    if ctx.voice_client:
      await ctx.voice_client.disconnect()
      await ctx.send('Saindo do canal.')

  @commands.command(aliases=['c'])
  async def clear(self, ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
      ctx.voice_client.stop()
      await ctx.send('Parando de tocar.')

  @commands.command()
  async def current(self, ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
      current_track = self._tracks[self._current_track_idx]
      await ctx.send(f"\"{current_track.title}\" "
                     f"(Faixa {self._current_track_idx}) está atualmente "
                     "tocando.")

  @commands.command(aliases=['l'])
  async def list(self, ctx):
    music_list_str = '\n'.join([f"{i} | {t.title}" for i, t in
                                enumerate(self._tracks)])
    await ctx.send(f'Músicas na lista: \n' + music_list_str)

  @play.before_invoke
  async def ensure_voice(self, ctx):
    if ctx.voice_client is None:
      if ctx.author.voice:
        await ctx.author.voice.channel.connect()
      else:
        await ctx.send("Você não está conectado a um canal de voz.")
    elif ctx.voice_client.is_playing():
      ctx.voice_client.stop()
