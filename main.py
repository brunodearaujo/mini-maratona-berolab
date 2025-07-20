# Ficheiro: main.py
# Autor: [O Seu Nome]
# Descrição: Ponto de entrada principal do jogo. Inicializa e executa o controlador do jogo.

from dino_runner.components.game import GameController

if __name__ == "__main__":
    # Cria uma instância do controlador principal do jogo.
    game = GameController()
    # Inicia o loop principal do jogo.
    game.execute()
