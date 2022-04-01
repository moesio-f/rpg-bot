import asyncio

import discord
import youtube_dl

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


class TrackSource(discord.PCMVolumeTransformer):
  ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause
    # issues sometimes
  }
  ffmpeg_options = {
    'executable': 'ffmpeg',
    'before_options': '-stream_loop -1',
    'options': '-vn'
  }
  ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

  def __init__(self, source, *, data, volume=0.5):
    super().__init__(source, volume)
    self.data = data

    self.title = data.get('title')
    self.url = data.get('url')

  @classmethod
  async def fetch_data(cls, url, loop=None, download=False):
    loop = loop or asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(
      url, download=download))

    if 'entries' in data:
      # take first item from a playlist
      data = data['entries'][0]

    return data

  @classmethod
  async def from_url(cls, url, *, loop=None, stream=False):
    loop = loop or asyncio.get_event_loop()
    data = await cls.fetch_data(url, loop=loop, download=not stream)

    filename = data['url'] if stream else cls.ytdl.prepare_filename(data)
    return cls(discord.FFmpegPCMAudio(filename, **cls.ffmpeg_options),
               data=data)
