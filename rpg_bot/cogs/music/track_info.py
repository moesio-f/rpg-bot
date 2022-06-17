import typing


class TrackInfo:
  def __init__(self, url: str,
               title: typing.Optional[str] = None,
               duration: typing.Optional[str] = None):
    self.url = url
    self.title = title
    self.duration = duration
