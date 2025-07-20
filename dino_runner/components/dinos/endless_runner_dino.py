# Ficheiro: dino_runner/components/dinos/endless_runner_dino.py
# Autor: [Bruno]
# Descrição: Define a classe do personagem principal para o modo de jogo "Endless Runner".
#            Esta classe gereia o estado, o movimento (pulo, agachar) e as animações do dinossauro.

import pygame

class EndlessRunnerDino:
    """
    Representa o dinossauro no modo Endless Runner, controlando a sua física,
    estados e animações.
    """
    # --- Constantes de Física ---
    # Estas constantes definem o comportamento do movimento do dinossauro.
    X_POS = 80             # Posição horizontal fixa do dinossauro no ecrã.
    Y_POS = 310            # Posição vertical do dinossauro quando está a correr (no "chão").
    Y_POS_DUCK = 340       # Posição vertical quando está agachado.
    JUMP_VELOCITY = 36.5   # Força inicial do pulo (valor alto para um pulo rápido e forte).
    GRAVITY = 3            # Força da gravidade que puxa o dinossauro para baixo.
    FAST_FALL_GRAVITY = 3  # Gravidade adicional aplicada ao agachar no ar para uma queda mais rápida.

    def __init__(self, assets, first_run=False):
        """
        Inicializa o dinossauro.
        
        Args:
            assets (AssetManager): O gestor de assets para carregar as imagens.
            first_run (bool): True se for a primeira vez que o jogo corre, para mostrar o dino parado.
        """
        # Carrega todas as imagens necessárias do AssetManager.
        self.assets = assets
        self.running_img = self.assets.get_image("DINO_RUNNING")
        self.jumping_img = self.assets.get_image("DINO_JUMP")
        self.ducking_img = self.assets.get_image("DINO_DUCKING")
        self.dead_img = self.assets.get_image("DINO_DEAD")
        self.start_img = self.assets.get_image("DINO_START")

        # --- Estado Inicial ---
        # Controla o comportamento atual do dinossauro.
        self.is_waiting = first_run  # Está à espera do primeiro input para começar a correr?
        self.is_running = not first_run
        self.is_jumping = False
        self.is_ducking = False
        self.is_dead = False

        # --- Atributos de Movimento e Animação ---
        self.jump_vel = self.JUMP_VELOCITY  # Velocidade vertical atual do pulo.
        # Define a imagem inicial: a de "start" se estiver à espera, ou a primeira de corrida.
        self.image = self.start_img if self.is_waiting else self.running_img[0]
        self.dino_rect = self.image.get_rect(x=self.X_POS, y=self.Y_POS)
        self.step_index = 0  # Usado para ciclar entre as frames da animação.

    def update(self):
        """Atualiza o estado do dinossauro a cada frame (movimento e animação)."""
        # Se o dinossauro estiver morto ou à espera, não faz nenhuma atualização.
        if self.is_dead or self.is_waiting:
            return

        # --- Gereciamento de Animação e Estado ---
        # Define a imagem correta com base no estado atual.
        if self.is_jumping:
            self.image = self.jumping_img
            # Lógica para agachar durante o pulo.
            if self.is_ducking:
                original_center = self.dino_rect.center
                self.image = self.ducking_img[1] # Usa a segunda imagem de agachado.
                self.dino_rect = self.image.get_rect(center=original_center)
        elif self.is_ducking:
            self.duck_animation()
        elif self.is_running:
            self.run_animation()
        
        # --- Física do Pulo ---
        if self.is_jumping:
            self.dino_rect.y -= self.jump_vel
            self.jump_vel -= self.GRAVITY
            # Se estiver agachado no ar, aplica a gravidade extra para cair mais rápido.
            if self.is_ducking:
                self.jump_vel -= self.FAST_FALL_GRAVITY

        # --- Lógica de Pouso ---
        # Verifica se o dinossauro tocou no chão após um pulo.
        if self.is_jumping and self.dino_rect.y >= self.Y_POS:
            self.is_jumping = False
            self.jump_vel = self.JUMP_VELOCITY # Reseta a velocidade do pulo.
            # Se a tecla de agachar estiver pressionada ao aterrar, entra no estado de agachado.
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                self.set_duck_state()
            else:
                self.set_run_state()

    def run_animation(self):
        """Cicla entre as imagens de corrida para criar a animação."""
        # Usa o step_index para alternar entre as duas imagens de corrida.
        self.image = self.running_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect(x=self.X_POS, y=self.Y_POS)
        self.step_index = (self.step_index + 1) % 10 # O ciclo vai de 0 a 9.

    def duck_animation(self):
        """Cicla entre as imagens de agachado para criar a animação."""
        self.image = self.ducking_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect(x=self.X_POS, y=self.Y_POS_DUCK)
        self.step_index = (self.step_index + 1) % 10

    # --- Métodos de Mudança de Estado ---
    # Estas funções são chamadas para alterar o estado do dinossauro.

    def set_run_state(self):
        """Define o estado do dinossauro para 'a correr'."""
        self.image = self.running_img[0]
        self.dino_rect = self.image.get_rect(x=self.X_POS, y=self.Y_POS)
        self.is_running = True
        self.is_ducking = False

    def set_duck_state(self):
        """Define o estado do dinossauro para 'agachado'."""
        self.image = self.ducking_img[0]
        self.dino_rect = self.image.get_rect(x=self.X_POS, y=self.Y_POS_DUCK)
        self.is_ducking = True
        self.is_running = False

    def jump(self):
        """Inicia a ação de pular."""
        # Se o jogo estava à espera, o primeiro pulo inicia a corrida.
        if self.is_waiting:
            self.is_waiting = False
            self.is_running = True
        
        # Só pode pular se não estiver já a pular.
        if not self.is_jumping:
            self.jump_vel = self.JUMP_VELOCITY
            self.is_jumping = True
            self.is_running = False
            self.is_ducking = False

    def duck(self):
        """Inicia a ação de agachar."""
        # Se estiver a pular, agachar acelera a queda.
        if self.is_jumping:
            self.is_ducking = True
            # Zera a velocidade ascendente para iniciar a queda imediatamente.
            if self.jump_vel > 0:
                self.jump_vel = 0
        # Se estiver a correr, simplesmente entra no estado de agachado.
        elif self.is_running:
            self.set_duck_state()

    def unduck(self):
        """Termina a ação de agachar."""
        # Se estava agachado no ar, volta à imagem de pulo normal.
        if self.is_jumping:
            self.is_ducking = False
            original_center = self.dino_rect.center
            self.image = self.jumping_img
            self.dino_rect = self.image.get_rect(center=original_center)
        # Se estava agachado no chão, volta a correr.
        else:
            self.set_run_state()

    def die(self):
        """Define o estado do dinossauro para 'morto'."""
        self.image = self.dead_img
        self.is_dead = True

    def draw(self, screen):
        """Desenha o dinossauro no ecrã."""
        screen.blit(self.image, self.dino_rect)
