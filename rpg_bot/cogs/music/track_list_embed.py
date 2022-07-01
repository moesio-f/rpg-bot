import typing
import enum
import math

import discord

from rpg_bot.cogs.music import track_info, ost_key


class Page(enum.Enum):
    HOME = 0
    TRACKS = 1


class TrackPage:
    def __init__(self, tracks: typing.List[track_info.TrackInfo],
                 key: ost_key.OSTKey,
                 entries: int = 10):
        self.tracks = tracks
        self.key = key
        self.info: ost_key.OSTKeyInfo = key.value

        self._entries = entries
        self._page = 0
        self._last_page = max(math.ceil(len(self.tracks)/10) - 1, 0)

    def total_tracks(self) -> int:
        return len(self.tracks)

    def has_previous_page(self) -> bool:
        return self._page > 0

    def has_next_page(self) -> bool:
        return self._page < self._last_page

    def current_page(self) -> typing.Tuple[typing.List[track_info.TrackInfo], int, int]:
        start = self._entries * self._page
        end = min(start + self._entries, len(self.tracks))

        return self.tracks[start:end], self._page, self._last_page

    def next_page(self):
        self._page += 1
        self._page = min(self._page, self._last_page)

    def previous_page(self):
        self._page -= 1
        self._page = max(self._page, 0)

    def entries_per_page(self):
        return self._entries


class EmbedContent(typing.NamedTuple):
    embed: discord.Embed
    content: str
    reactions: typing.List[str]
    clear_reactions: bool
    page: Page


class TrackListEmbedManager:
    HOME_EMOJI = "🔷"
    NEXT_EMOJI = "▶️"
    PREV_EMOJI = "◀️"
    HOME_THUMB = "https://d1fdloi71mui9q.cloudfront.net/f6wXXt6ZRqaoiLrCJqfe_7Hsx2OQ00B7v3ya3"

    def __init__(self, tracks: typing.Dict[ost_key.OSTKey, typing.List[track_info.TrackInfo]]):
        self._tracks = tracks
        self._current_page = Page.HOME
        self._track_page: TrackPage = None
        self._color = None

        self._ost_keys_info: typing.List[ost_key.OSTKeyInfo] = []
        self._ost_keys_info = [k.value for k in ost_key.OSTKey]
        self._ost_keys_emoji = list(map(lambda i: i.emoji,
                                        self._ost_keys_info))

    def home(self) -> EmbedContent:
        t = sum([len(l) for _, l in self._tracks.items()])
        self._color = discord.Color.dark_blue()
        e = discord.Embed(title='Lista de Músicas',
                          description='Reaja para obter a lista de músicas cadastradas no grupo.',
                          color=self._color)
        e.set_footer(text="Para voltar ao início use "
                     f"{TrackListEmbedManager.HOME_EMOJI} | "
                     f"Total de Músicas: {t}")
        e.set_thumbnail(url=TrackListEmbedManager.HOME_THUMB)
        reactions = [TrackListEmbedManager.HOME_EMOJI]

        for i in self._ost_keys_info:
            e.add_field(name=f'{i.name} {i.emoji}',
                        value=f'{i.desc}',
                        inline=False)
            reactions.append(i.emoji)

        return EmbedContent(embed=e,
                            content="",
                            reactions=reactions,
                            clear_reactions=True,
                            page=Page.HOME)

    def track_page(self, emoji) -> EmbedContent:
        for k in ost_key.OSTKey:
            if emoji == k.value.emoji:
                self._color = discord.Color.random()
                self._track_page = TrackPage(self._tracks[k], k)
                return self._show_track_page()

    def react(self, emoji) -> EmbedContent:
        if emoji == TrackListEmbedManager.HOME_EMOJI:
            self._current_page = Page.HOME
            return self.home()
        elif emoji in [TrackListEmbedManager.NEXT_EMOJI,
                       TrackListEmbedManager.PREV_EMOJI] \
                and self._current_page == Page.TRACKS:
            self._current_page = Page.TRACKS
            if emoji == TrackListEmbedManager.NEXT_EMOJI:
                return self._next_track_page()
            else:
                return self._previous_track_page()
        elif emoji in self._ost_keys_emoji:
            self._current_page = Page.TRACKS
            return self.track_page(emoji)

    def _next_track_page(self) -> EmbedContent:
        if self._track_page.has_next_page():
            self._track_page.next_page()
        return self._show_track_page()

    def _previous_track_page(self) -> EmbedContent:
        if self._track_page.has_previous_page():
            self._track_page.previous_page()
        return self._show_track_page()

    def _show_track_page(self) -> EmbedContent:
        tracks, p, l = self._track_page.current_page()
        info = self._track_page.info
        key = self._track_page.key
        t = self._track_page.total_tracks()
        offset = self._track_page.entries_per_page() * p

        e = discord.Embed(title=f'{info.name}',
                          description=f'{info.desc}',
                          color=self._color)
        reactions = [TrackListEmbedManager.HOME_EMOJI]
        e.set_footer(text=f"Página {p+1}/{l+1} | Total de Músicas: {t}")

        for i, t in enumerate(tracks):
            e.add_field(name=f'{t.title} ({t.duration})',
                        value=f'Faixa [{key.name}{i+1+offset}]({t.url})',
                        inline=False)

        if self._track_page.has_next_page():
            reactions.append(TrackListEmbedManager.NEXT_EMOJI)

        if self._track_page.has_previous_page():
            reactions.append(TrackListEmbedManager.PREV_EMOJI)

        return EmbedContent(embed=e,
                            content="",
                            reactions=reactions,
                            clear_reactions=True,
                            page=Page.TRACKS)
