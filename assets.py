import pygame
from constants import WIDTH, HEIGHT

class AssetLoader:
    @staticmethod
    def load_images():
        # Load and scale all game images
        return {
            'intro_bg': pygame.transform.scale(pygame.image.load("images/intro_bg.jpg"), (WIDTH, HEIGHT)),
            'game_bg': pygame.transform.scale(pygame.image.load("images/background.jpg"), (WIDTH, HEIGHT)),
            'hole': pygame.transform.scale(pygame.image.load("images/hole.png"), (200, 150)),
            'hammer': pygame.transform.scale(pygame.image.load("images/hammer.png"), (80, 80))
        }

    @staticmethod
    def load_zombie_frames(color):
        idle = [
            pygame.image.load(f"assets/{color}/idle/frame-1.png"),
            pygame.image.load(f"assets/{color}/idle/frame-2.png"),
        ]
        dead = [
            pygame.image.load(f"assets/{color}/got-hit/frame-1.png"),
            pygame.image.load(f"assets/{color}/got-hit/frame-2.png"),
        ]

        idle = [pygame.transform.scale(img, (120,150)) for img in idle]
        dead = [pygame.transform.scale(img, (120,150)) for img in dead]

        return {"idle": idle, "dead": dead}

    @staticmethod
    def load_sounds():
        # Load sound effects
        pygame.mixer.music.load("assets/sound/background-theme.mp3")
        boing_sound = pygame.mixer.Sound("assets/sound/Cartoon Boing.mp3")
        return boing_sound

    @staticmethod
    def load_fonts():
        return {
            'large': pygame.font.SysFont(None, 80),
            'small': pygame.font.SysFont(None, 40)
        }
