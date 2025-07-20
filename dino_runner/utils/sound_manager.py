import pygame
import os

class SoundManager:
    def __init__(self, settings):
        self.sfx_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "sfx")
        self.music_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "music")
        self.sounds = {}
        self.settings = settings # Armazena as configurações do jogo
        self._load_sounds()

    def _load_sound(self, name, filename):
        full_path = os.path.join(self.sfx_dir, filename)
        try:
            self.sounds[name] = pygame.mixer.Sound(full_path)
        except pygame.error:
            print(f"Aviso: Não foi possível carregar o som: {full_path}")
            self.sounds[name] = None

    def _load_sounds(self):
        self._load_sound("pistol_shot", "pistol_shot.wav")
        self._load_sound("sword_slash", "sword_slash.wav")
        self._load_sound("player_hit", "player_hit.wav")

    def play(self, name, volume=0.5):
        """Reproduz um efeito sonoro se o SFX estiver ativado."""
        if self.settings['sfx'] and name in self.sounds and self.sounds[name]:
            sound = self.sounds[name]
            sound.set_volume(volume)
            sound.play()

    def play_music(self, filename, volume=0.4):
        """Carrega e reproduz uma música de fundo em loop se a música estiver ativada."""
        if not self.settings['music']:
            return
            
        full_path = os.path.join(self.music_dir, filename)
        try:
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1) # -1 para tocar em loop infinito
        except pygame.error:
            print(f"Aviso: Não foi possível carregar a música: {full_path}")

    def stop_music(self):
        """Para a música de fundo."""
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
