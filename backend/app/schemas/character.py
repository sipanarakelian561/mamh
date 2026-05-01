from typing import Literal

from pydantic import BaseModel


MonsterChoice = Literal["monster", "dog", "dinosaur"]


class CharacterStateOut(BaseModel):
    starter_monster: MonsterChoice | None = None
    equipped_monster: MonsterChoice | None = None
    starter_selected: bool
    available_starters: list[MonsterChoice]


class CharacterSelectRequest(BaseModel):
    monster: MonsterChoice
