# Ficheiro: dino_runner/utils/asset_manager.py
# Descrição: Classe centralizada para carregar e gerir todos os assets (imagens e fontes).
import pygame
import os
from dino_runner.utils.constants import FONT_PATH # Importa o caminho da fonte

class AssetManager:
    """Carrega todos os recursos visuais e de texto uma única vez."""
    def __init__(self):
        self.assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        self.images = {}
        self.fonts = {}
        self._load_assets()

    def _load_image(self, name, path, convert_alpha=True):
        """Função auxiliar para carregar e otimizar uma imagem."""
        full_path = os.path.join(self.assets_dir, path)
        try:
            image = pygame.image.load(full_path)
            # Armazena a imagem carregada no dicionário
            self.images[name] = image.convert_alpha() if convert_alpha else image.convert()
            # Retorna a imagem para uso imediato (ex: ao criar listas)
            return self.images[name]
        except pygame.error:
            print(f"AVISO: Imagem não encontrada em '{full_path}'. A usar um placeholder.")
            placeholder = pygame.Surface((50, 50)); placeholder.fill((255, 0, 255))
            self.images[name] = placeholder
            return placeholder

    def _load_font(self, name, path, size):
        """Função auxiliar para carregar uma fonte."""
        self.fonts[name] = pygame.font.Font(path, size)

    def _load_assets(self):
        """Carrega todas as imagens e fontes do jogo."""
        
        # --- Assets Gerais e do Modo Normal ---
        self._load_image("ICON", "DinoWallpaper.png")
        self._load_image("BG", "Other/Track.png")
        self._load_image("CLOUD", "Other/Cloud.png")
        self._load_image("HEART", "Other/SmallHeart.png")
        self._load_image("SHIELD_ICON", "Other/shield.png")
        self._load_image("HAMMER_ICON", "Other/hammer.png")

        # --- Dinossauro (Modo Normal) ---
        self._load_image("DINO_START", "Dino/DinoStart.png")
        self._load_image("DINO_JUMP", "Dino/DinoJump.png")
        self._load_image("DINO_DEAD", "Dino/DinoDead.png")
        self.images["DINO_RUNNING"] = [
            self._load_image("DINO_RUN1", "Dino/DinoRun1.png"),
            self._load_image("DINO_RUN2", "Dino/DinoRun2.png")
        ]
        self.images["DINO_DUCKING"] = [
            self._load_image("DINO_DUCK1", "Dino/DinoDuck1.png"),
            self._load_image("DINO_DUCK2", "Dino/DinoDuck2.png")
        ]

        # --- Obstáculos (Modo Normal) ---
        self.images["SMALL_CACTUS"] = [
            self._load_image("SMALL_CACTUS_1", "Cactus/SmallCactus1.png"),
            self._load_image("SMALL_CACTUS_2", "Cactus/SmallCactus2.png"),
            self._load_image("SMALL_CACTUS_3", "Cactus/SmallCactus3.png"),
        ]
        self.images["LARGE_CACTUS"] = [
            self._load_image("LARGE_CACTUS_1", "Cactus/LargeCactus1.png"),
            self._load_image("LARGE_CACTUS_2", "Cactus/LargeCactus2.png"),
            self._load_image("LARGE_CACTUS_3", "Cactus/LargeCactus3.png"),
        ]
        self.images["BIRD"] = [
            self._load_image("BIRD_1", "Bird/Bird1.png"),
            self._load_image("BIRD_2", "Bird/Bird2.png")
        ]
        
        # --- Personagem (Modo Roguelite) ---
        self._load_image("BERO_START", "Bero/Bero.png")
        self.images["BERO_RUNNING"] = [ self.images["BERO_START"], self.images["BERO_START"] ]
        
        # --- Inimigos e Armas (Modo Roguelite) ---
        self._load_image("BULLET", "weapons/fireball.png")
        self._load_image("ENEMY_BULLET", "weapons/enemy_bullet.png")
        self._load_image("SHARD", "weapons/shard.png")
        self._load_image("SWORD_SLASH", "weapons/sword_slash.png")

        # --- Inimigos do Caminho do Dino (Pistoleiro) ---
        self._load_image("CACTO1", "enemies/dino_path/cacto1.png")
        self._load_image("CACTO2", "enemies/dino_path/cacto2.png")
        self._load_image("BIRD1", "enemies/dino_path/bird1.png")
        self._load_image("BIRD2", "enemies/dino_path/bird2.png")
        self._load_image("CACTO3", "enemies/dino_path/cacto3.png") # Boss

        # --- Inimigos do Caminho do Bero (Espadachim) ---
        self._load_image("MIGUEL", "enemies/bero_path/miguel.png")
        self._load_image("PAM", "enemies/bero_path/pam.png")
        self._load_image("TEKI", "enemies/bero_path/teki.png")
        self._load_image("DANN", "enemies/bero_path/dann.png")
        self._load_image("BERO", "enemies/bero_path/bero.png") # Boss

        # --- Fontes ---
        self._load_font("title", FONT_PATH, 24)
        self._load_font("body", FONT_PATH, 18)
        self._load_font("ui", FONT_PATH, 14)
        self._load_font("stats", FONT_PATH, 16)

    def get_image(self, name):
        """Retorna uma imagem carregada pelo nome."""
        return self.images.get(name)

    def get_font(self, name):
        """Retorna uma fonte carregada pelo nome."""
        return self.fonts.get(name)
