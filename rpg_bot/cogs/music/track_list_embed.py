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
        self._last_page = math.ceil(len(self.tracks)/10) - 1

    def has_previous_page(self) -> bool:
        return self._page > 0

    def has_next_page(self) -> bool:
        return self._page < self._last_page

    def current_page(self) -> typing.List[track_info.TrackInfo]:
        start = self._entries * self._page
        end = min(start + self._entries, len(self.tracks))

        return self.tracks[start:end]

    def next_page(self):
        self._page += 1
        self._page = min(self._page, self._last_page)

    def previous_page(self):
        self._page -= 1
        self._page = max(self._page, 0)


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

    def __init__(self, tracks: typing.Dict[ost_key.OSTKey, typing.List[track_info.TrackInfo]]):
        self._tracks = tracks
        self._current_page = Page.HOME
        self._track_page: TrackPage = None

        self._ost_keys_info: typing.List[ost_key.OSTKeyInfo] = []
        self._ost_keys_info = [k.value for k in ost_key.OSTKey]
        self._ost_keys_emoji = list(map(lambda i: i.emoji,
                                        self._ost_keys_info))

    def home(self) -> EmbedContent:
        e = discord.Embed(title='Lista de Músicas',
                          description='Reaja para obter a lista de músicas cadastradas no grupo.',
                          color=discord.Color.dark_blue())
        content = f"Para voltar a home reaja com {TrackListEmbedManager.HOME_EMOJI}"
        reactions = [TrackListEmbedManager.HOME_EMOJI]

        for i in self._ost_keys_info:
            e.add_field(name=f'{i.name}\t{i.emoji}',
                        value=f'{i.desc}',
                        inline=False)
            reactions.append(i.emoji)

        return EmbedContent(embed=e,
                            content=content,
                            reactions=reactions,
                            clear_reactions=True,
                            page=Page.HOME)

    def track_page(self, emoji) -> EmbedContent:
        for k in ost_key.OSTKey:
            if emoji == k.value.emoji:
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
        tracks = self._track_page.current_page()
        info = self._track_page.info
        key = self._track_page.key

        e = discord.Embed(title=f'{info.name}',
                          description=f'{info.desc}',
                          color=discord.Color.dark_green())
        content = ""
        reactions = [TrackListEmbedManager.HOME_EMOJI]

        for i, t in enumerate(tracks):
            e.add_field(name=f'{t.title} ({t.duration})',
                        value=f'Faixa [{key.name}{i+1}]({t.url})',
                        inline=False)

        if self._track_page.has_next_page():
            reactions.append(TrackListEmbedManager.NEXT_EMOJI)

        if self._track_page.has_previous_page():
            reactions.append(TrackListEmbedManager.PREV_EMOJI)

        return EmbedContent(embed=e,
                            content=content,
                            reactions=reactions,
                            clear_reactions=True,
                            page=Page.TRACKS)
