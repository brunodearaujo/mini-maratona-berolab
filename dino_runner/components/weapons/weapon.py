import pygame

class Weapon:
    def __init__(self, player):
        self.player = player
        self.last_attack_time = 0

    def attack(self):
        # Cada arma implementará sua própria lógica de ataque
        pass

    def update(self):
        # Algumas armas podem precisar de lógica de update (ex: recarga)
        pass

    def draw(self, screen):
        # A maioria das armas não precisa ser desenhada, mas seus efeitos sim
        pass