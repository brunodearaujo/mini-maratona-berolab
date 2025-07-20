# Ficheiro: dino_runner/components/powerups/Shield.py
# Autor: [O Seu Nome]
# Descrição: Define a classe para o power-up de Escudo no modo Endless Runner.

# Importa as constantes de imagem e tipo, e a classe base PowerUp.
from dino_runner.utils.constants import SHIELD, SHIELD_TYPE
from dino_runner.components.powerups import PowerUp


class Shield(PowerUp):
    """
    Representa o power-up de Escudo que pode aparecer no jogo.
    Herda da classe base PowerUp.
    """
    def __init__(self):
        """
        Inicializa o objeto de Escudo, definindo a sua imagem e tipo.
        """
        # Define a imagem específica para este power-up.
        self.image = SHIELD
        # Define o tipo de power-up, para que o jogo saiba como aplicar o seu efeito.
        self.type = SHIELD_TYPE
        
        # Chama o construtor da classe pai (PowerUp) para completar a inicialização.
        super().__init__(self.image, self.type)
