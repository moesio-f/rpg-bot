import enum
import typing


class OSTKey(enum.Enum):
  A = "Aparições"
  C = "Combate"
  D = "Drama"
  E = "Exploração"
  F = "Finalizando"
  H = "Heróicas"
  I = "Iniciando"
  S = "Sad"
  T = "Terror"
  W = "What?"

  @classmethod
  def from_str(cls, value: str):
    for k in cls:
      if value.upper() == str(k.name):
        return k
    return None


class KeyIndex(typing.NamedTuple):
  key: typing.Optional[OSTKey]
  index: int
