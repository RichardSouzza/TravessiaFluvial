class ExcessPassengersException(Exception):
    def __init__(self):
        super().__init__("São permitidos apenas 2 passageiros na embarcação.")


class FatherAndDaughtersAloneException(Exception):
    def __init__(self):
        super().__init__("O pai não ficar sozinho com as filhas.")


class MotherAndSonsAloneException(Exception):
    def __init__(self):
        super().__init__("A mãe não ficar sozinha com os filhos.")


class PilotAbsentException(Exception):
    def __init__(self):
        super().__init__("Não há piloto no barco.")


class PlayerNotExistException(Exception):
    def __init__(self, player: str):
        self.player = player
        self.message = f"O jogador \"{player}\" não existe."
        super().__init__(self.message)


class UnguardedThiefException(Exception):
    def __init__(self):
        super().__init__("O ladrão não pode ficar sozinho com nenhum integrante da família.")
