# Ficheiro: dino_runner/utils/constants.py
# Descrição: Contém constantes estáticas (valores, textos) usadas em todo o jogo.
import os

# --- Configurações da Tela e Jogo ---
TITLE = "Dino Runner - Bero Mode"
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
FPS = 30

# --- Caminhos (Paths) ---
# Define o caminho base para a pasta de assets
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
# Define o caminho completo para a fonte, para ser usado pelo AssetManager
FONT_PATH = os.path.join(ASSETS_DIR, "font", "PressStart2P-Regular.ttf")

# --- Tipos de Power-up (Exemplo do Modo Normal) ---
DEFAULT_TYPE = "default"
SHIELD_TYPE = "shield"
