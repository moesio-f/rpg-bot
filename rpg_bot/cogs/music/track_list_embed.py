from turtle import color, title
import typing
import enum

import discord

from rpg_bot.cogs.music import track_info, ost_key


class Page(enum.Enum):
    HOME = 0
    TRACKS = 1


class EmbedContent(typing.NamedTuple):
    embed: discord.Embed
    content: str
    reactions: typing.List[str]
    clear_reactions: bool
    page: Page


class TrackListEmbedManager:
    def __init__(self, tracks: typing.Dict[ost_key.OSTKey, typing.List[track_info.TrackInfo]]):
        self._tracks = tracks
        self._current_page = Page.HOME

    def home(self) -> EmbedContent:
        e = discord.Embed(title='Lista de Músicas',
                          description='Reaja para obter a lista de músicas cadastradas no grupo.',
                          color=discord.Color.dark_blue())
        content = "Para voltar a home reaja com 🔷"
        reactions = ["🔷"]

        for k in ost_key.OSTKey:
            i: ost_key.OSTKeyInfo = k.value
            e.add_field(name=f'{i.name}\t{i.emoji}', value=f'{i.desc}', inline=False)
            reactions.append(i.emoji)

        return EmbedContent(embed=e,
                            content=content,
                            reactions=reactions,
                            clear_reactions=True,
                            page=Page.HOME)
