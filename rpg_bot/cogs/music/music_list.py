import typing
import collections

from discord.ext import commands
from spotdl.search import song_gatherer

from rpg_bot import utils
from rpg_bot.cogs.music import track_source, track_info, ost_key


class MusicList(commands.Cog):
  def __init__(self, bot, urls: typing.Dict[ost_key.OSTKey, typing.List[str]]):
    self._bot = bot
    self._tracks = {k: [track_info.TrackInfo(url=u) for u in lu]
                    for k, lu in urls.items()}
    self._current_track: ost_key.KeyIndex = ost_key.KeyIndex(key=None, index=-1)
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
      for k in ost_key.OSTKey:
        for track in self._tracks[k]:
          self._update_url_if_spotify(track)
          data = await track_source.TrackSource.fetch_data(track.url,
                                                           loop=self._bot.loop,
                                                           download=False)
          track.title = data.get('title')
      self._tracks_info_initialized = True

  @commands.command(aliases=['a'])
  async def add(self, ctx, t: str, url: str):
    key = ost_key.OSTKey.from_str(t)

    if key is None:
      return await ctx.send(f'{t} não é um tipo de OST válido.')

    track = track_info.TrackInfo(url=url)
    self._update_url_if_spotify(track)
    data = await track_source.TrackSource.fetch_data(track.url,
                                                     loop=self._bot.loop,
                                                     download=False)
    track.title = data.get('title')
    self._tracks[key].append(track)
    await ctx.send(f'Faixa \"{track.title}\" adicionada.')

  @commands.command(aliases=['r', 'rem'])
  async def remove(self, ctx, value: str):
    key = ost_key.OSTKey.from_str(value[0])
    index = int(value[1:]) - 1

    if key is None or index not in range(len(self._tracks[key])):
      return await ctx.send(f'Faixa inválida.')

    title = self._tracks[key][index].title
    del self._tracks[key][index]
    await ctx.send(f'Faixa \"{title}\" ({key.name}{index}) removida.')

  @commands.command(aliases=['p'])
  async def play(self, ctx, value: str):
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

    await ctx.send('Tocando '
                   f'{key.name}{index + 1}: '
                   f'\"{self._tracks[key][index].title}\" '
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
      k = self._current_track.key
      i = self._current_track.index
      current_track = self._tracks[k][i]
      await ctx.send(f"\"{current_track.title}\" "
                     f"(Faixa {k.name}{i + 1}) está atualmente "
                     "tocando.")

  @commands.command(aliases=['l'])
  async def list(self, ctx):
    ordered_dict = collections.OrderedDict(sorted(self._tracks.items(),
                                                  key=lambda k: str(k[0].name)))
    music_list_str = '\n'.join(filter(None,
                                      ['\n'.join([f"{k.name}{i + 1}:\t{t.title}"
                                                  for i, t in
                                                  enumerate(self._tracks[k])])
                                       for k, lti in ordered_dict.items()]))
    await ctx.send(f'Músicas na lista: \n' + f"```{music_list_str}```")

  @play.before_invoke
  async def ensure_voice(self, ctx):
    if ctx.voice_client is None:
      if ctx.author.voice:
        await ctx.author.voice.channel.connect()
      else:
        await ctx.send("Você não está conectado a um canal de voz.")
    elif ctx.voice_client.is_playing():
      ctx.voice_client.stop()
