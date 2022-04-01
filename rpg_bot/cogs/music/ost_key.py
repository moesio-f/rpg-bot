import enum
import typing


class OSTKey(enum.Enum):
  N = "Iniciando"
  E = "Exploração"
  C = "Combate"
  A = "Aparições"
  H = "Heróicas"
  D = "Drama"
  T = "Tristes"
  W = "What?"
  F = "Finalizando"

  @classmethod
  def from_str(cls, value: str):
    for k in cls:
      if value.upper() == str(k.name):
        return k
    return None


class KeyIndex(typing.NamedTuple):
  key: typing.Optional[OSTKey]
  index: int
