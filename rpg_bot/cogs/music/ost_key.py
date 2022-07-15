import enum
import typing


class OSTKeyInfo:
    def __init__(self, name: str, desc=None, emoji=None):
        self.name = name
        self.desc = desc
        self.emoji = emoji


class OSTKey(enum.Enum):
    A = OSTKeyInfo("Aparição", emoji="🇦",
                   desc="OST's para quando algum personagem mais importante aparecer")
    C = OSTKeyInfo("Combate", emoji="🇨",
                   desc="OST's para quando os jogadores entrarem em combate")
    D = OSTKeyInfo("Drama", emoji="🇩",
                   desc="OST's para quando algum personagem estiver perto de morrer ou alguma situação de risco")
    E = OSTKeyInfo("Exploração", emoji="🇪",
                   desc="OST's para quando os jogadores estiverem explorando")
    F = OSTKeyInfo("Finalizando", emoji="🇫",
                   desc="OST's para quando a sessão estiver chegando ao seu final")
    H = OSTKeyInfo("Heróica", emoji="🇭",
                   desc="OST's para um momento Heróico")
    I = OSTKeyInfo("Iniciando", emoji="🇮",
                   desc="OST's para início da sessão")
    L = OSTKeyInfo("Lamentável", emoji="🇱",
                   desc="OST's para quando algum momento mais emocionante estiver acontecendo")
    Q = OSTKeyInfo("Quimera", emoji="🇶",
                   desc="OST's para encontro com quimeras")
    T = OSTKeyInfo("Terror", emoji="🇹",
                   desc="OST's para momentos de terror e/ou assustadores")
    R = OSTKeyInfo("Revelação", emoji="🇷",
                   desc="OST's para momentos de revelação")

    @classmethod
    def from_str(cls, value: str):
        for k in cls:
            if value.upper() == str(k.name):
                return k
        return None


class KeyIndex(typing.NamedTuple):
    key: typing.Optional[OSTKey]
    index: int
