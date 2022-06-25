import enum
import typing


class OSTKeyInfo:
    def __init__(self, name: str, desc=None, emoji=None):
        self.name = name
        self.desc = desc
        self.emoji = emoji


class OSTKey(enum.Enum):
    A = OSTKeyInfo("Aparições", emoji=":regional_indicator_a:")
    C = OSTKeyInfo("Combate", emoji=":regional_indicator_c:")
    D = OSTKeyInfo("Drama", emoji=":regional_indicator_d:")
    E = OSTKeyInfo("Exploração", emoji=":regional_indicator_e:")
    F = OSTKeyInfo("Finalizando", emoji=":regional_indicator_f:")
    H = OSTKeyInfo("Heróicas", emoji=":regional_indicator_h:")
    I = OSTKeyInfo("Iniciando", emoji=":regional_indicator_i:")
    S = OSTKeyInfo("Sad", emoji=":regional_indicator_s:")
    T = OSTKeyInfo("Terror", emoji=":regional_indicator_t:")
    W = OSTKeyInfo("What?", emoji=":regional_indicator_w:")
    Q = OSTKeyInfo("Quimera", emoji=":regional_indicator_q:")

    @classmethod
    def from_str(cls, value: str):
        for k in cls:
            if value.upper() == str(k.name):
                return k
        return None


class KeyIndex(typing.NamedTuple):
    key: typing.Optional[OSTKey]
    index: int
