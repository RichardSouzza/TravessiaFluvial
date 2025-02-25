from copy import copy
from re import search
from typing import List

from colorama import init
from termcolor import colored

from exceptions import *


init()


kinships = {
    1: "Pai",
    2: "Mãe",
    3: "Filha",
    4: "Filho",
    5: "Guarda",
    6: "Ladrão",
}


class Player:
    def __init__(self, key: str, kinship: int, color) -> None:
        self.key = key
        self.char = f" {key} "
        self.kinship = kinship
        self.can_drive = True if kinship in [1, 2, 5] else False
        self.color = color
        self.layer = 0

    def move(self) -> None:
        self.layer = (self.layer - 1) * -1

    def __str__(self) -> str:
        return colored(self.char, None, self.color)


class Boat:
    def __init__(self) -> None:
        self.layer = 0

    def move(self) -> None:
        self.layer = (self.layer - 1) * -1

    def __str__(self) -> str:
        return colored(" ⛵ ", None, None)


class Game:
    def __init__(self):
        p   = Player("P", 1, "on_blue")
        m   = Player("M", 2, "on_yellow")
        fa1 = Player("a", 3, "on_magenta")
        fa2 = Player("e", 3, "on_magenta")
        fo1 = Player("i", 4, "on_cyan")
        fo2 = Player("o", 4, "on_cyan")
        g   = Player("G", 5, "on_green")
        l   = Player("L", 6, "on_red")

        self.boat = Boat()

        self.group_players = [p, m, fa1, fa2, fo1, fo2, g, l]
        self.moves_count = 0

    def create_group_copy(self) -> None:
        self.copy_group_players = [copy(player) for player in self.group_players]

    def get_player_by_key(self, group: List[Player], key: str) -> Player | None:
        player_list: List[Player] = list(filter(lambda x: x.key == key, group))
        if len(player_list) > 0:
            return player_list[0]

    def get_players_by_layer(self, group: List[Player], layer: int) -> List[Player]:
        return list(filter(lambda x: x.layer == layer, group))

    def validate_boat(self, action: str) -> None:
        if len(action) > 2: # Há mais que 2 passageiros no barco?
            raise ExcessPassengersException()

        has_daughter = has_driver = has_father = has_guard = has_mother = has_son = has_thief = False

        if search(r"(.)\1", action): # Há passageiros repetidos?
            raise RepeatedPlayerException()

        for key in action:
            player = self.get_player_by_key(self.group_players, key)

            if player == None: # O passageiro fornecido existe?
                raise PlayerNotExistException(key)

            if player.layer != self.boat.layer: # O barco e o passageiro estão na mesma margem?
                raise InaccessibleBoatException(key)

            has_daughter = True if player.kinship == 3 else has_daughter
            has_driver   = True if player.can_drive    else has_driver
            has_father   = True if player.kinship == 1 else has_father
            has_guard    = True if player.kinship == 5 else has_guard
            has_mother   = True if player.kinship == 2 else has_mother
            has_son      = True if player.kinship == 4 else has_son
            has_thief    = True if player.kinship == 6 else has_thief

        if not has_driver: # Não há piloto no barco?
            raise PilotAbsentException()

        if has_thief and not has_guard: # Há ladrão desguardado no barco?
            raise UnguardedThiefException()

        if has_father and has_daughter and not has_mother: # O pai está sozinho com as filhas?
            raise FatherAndDaughtersAloneException()

        if has_mother and has_son and not has_father: # A mãe está sozinha com os filhos?
            raise MotherAndSonsAloneException()

    def validate_layers(self):
        has_daughter = has_father = has_guard = has_mother = has_son = has_thief = False

        for layer in range(2):
            for player in self.get_players_by_layer(self.copy_group_players, layer):
                has_daughter = True if player.kinship == 3 else has_daughter
                has_father   = True if player.kinship == 1 else has_father
                has_guard    = True if player.kinship == 5 else has_guard
                has_mother   = True if player.kinship == 2 else has_mother
                has_son      = True if player.kinship == 4 else has_son
                has_thief    = True if player.kinship == 6 else has_thief

            # O ladrão está sozinho com um integrante família?
            if (has_thief
                and any((has_father, has_mother, has_daughter, has_son))
                and not has_guard
            ):
                raise UnguardedThiefException()

            if has_father and has_daughter and not has_mother: # O pai está sozinho com as filhas?
                raise FatherAndDaughtersAloneException()

            if has_mother and has_son and not has_father: # A mãe está sozinha com os filhos?
                raise MotherAndSonsAloneException()

            has_daughter = has_father = has_guard = has_mother = has_son = has_thief = False

    def move(self, group: List[Player], player_key: str) -> None:
        player = self.get_player_by_key(group, player_key)
        if player: player.move()

    def read_input(self) -> None:
        self.create_group_copy()
        action = input(":")

        try:
            self.validate_boat(action) # Validation upon boarding
        except Exception as exception:
            return print(exception)

        for player in action:
            self.move(self.copy_group_players, player) # Simulate move

        try:
            self.validate_layers() # Validation upon boarding # Validation upon landing
        except Exception as exception:
            return print(exception)

        self.boat.move()
        for player in action:
            self.move(self.group_players, player) # Real move
        self.moves_count += 1


    def check_win(self) -> bool:
        players_on_top = self.get_players_by_layer(self.group_players, 1)
        if len(players_on_top) == len(self.group_players):
            return True
        return False

    def win(self) -> None:
        self.render()
        print("\nVocê venceu!")
        print(f"{self.moves_count} travessias foram realizadas.")
        quit()

    def render(self) -> None:
        top_layer    = filter(lambda x: x.layer == 1, self.group_players)
        bottom_layer = filter(lambda x: x.layer == 0, self.group_players)

        """
         __________________
        |      LAYOUT      |
      1 |——————————————————|
      2 |          [][][][]| players
      3 |        //        | boat
      4 |                  |
      5 |~~~~~~~~~~~~~~~~~~| river
      6 |                  |
      7 |        //        | boat
      8 |[][][][]          | players
      9 |:                 | input
     10 |                  | ?error
        |__________________|
        """

        print("—" * 60) # Line 1

        print("   " * len(self.group_players), end="") # Line 2
        for player in top_layer:                           #
            print(player, end="")                          #
        print()                                            #

        if self.boat.layer == 1:                   # Line 3
            print(f"{str(self.boat): ^60}") #
        else: print()                              #

        print("\n" + "🌊" * 30, end="\n\n") # Lines 4, 5 and 6

        if self.boat.layer == 0:                   # Line 7
            print(f"{str(self.boat): ^60}") #
        else: print()                              #

        for player in bottom_layer: # Line 8
            print(player, end="")   #
        print()                     #

    def run(self) -> None:
        while True:
            self.render()
            self.read_input()
            if self.check_win():
                self.win()


if __name__ == "__main__":
    game = Game()
    game.run()