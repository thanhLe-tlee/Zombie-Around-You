import pygame, sys, random
from pygame.locals import *

pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 1100, 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Zombie:
    def __init__(self, frames, holes, game):
        self.frames = frames  # {"idle": [...], "dead": [...]}
        self.holes = holes
        self.game = game

        self.state = "idle"
        self.frame_index = 0
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_rect()

        self.animation_timer = 0
        self.animation_speed = 200  

        self.active = False
        self.rising = False
        self.falling = False
        self.speed = 5 
        self.base_y = -50
        self.target_y = 0

        self.idle_timer = 0
        self.idle_duration = 1000
        self.cooldown_timer = 0
        self.cooldown_duration = random.randint(500, 1500)
        self.reset()

    def reset(self):
        self.active = False
        self.rect.topleft = (-200, 200)

    def spawn(self):
        available = [h for h in self.holes if h not in self.game.occupied_holes]
        if not available: 
            return
        self.active = True
        pos = random.choice(available)
        self.rect.midbottom = (pos[0] + 100, pos[1] + 120)

        self.current_hole = pos
        self.game.occupied_holes.add(pos)
        
        self.base_y = self.rect.bottom
        self.target_y = self.base_y - 40
        self.rising = True
        self.falling = False
        self.idle_timer = 0

    def update(self, dt):
        if not self.active:
            self.cooldown_timer += dt
            if self.cooldown_timer >= self.cooldown_duration:
                self.spawn()
            return

        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames[self.state])
            self.image = self.frames[self.state][self.frame_index]

        if self.rising:
            if self.rect.bottom > self.target_y:
                self.rect.bottom -= self.speed
            else: 
                self.rising = False
                self.idle_timer = 0
        elif not self.rising and not self.falling:
            self.idle_timer += dt
            if self.idle_timer >= self.idle_duration:
                self.falling = True

        elif self.falling:
            if self.rect.bottom < self.base_y:
                self.rect.bottom += self.speed
            else:
                self.falling = False
                self.active = False 
                if hasattr(self, "current_hole"):
                    self.game.occupied_holes.discard(self.current_hole)

    def draw(self, screen):
        if self.active:
            screen.blit(self.image, self.rect)


class WhackAZombie:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Whack a Zombie")
        self.clock = pygame.time.Clock()

        # Load assets
        self.intro_bg = pygame.transform.scale(pygame.image.load("images/intro_bg.jpg"), (WIDTH, HEIGHT))
        self.game_bg = pygame.transform.scale(pygame.image.load("images/background.jpg"), (WIDTH, HEIGHT))
        self.hole_img = pygame.transform.scale(pygame.image.load("images/hole.png"), (200, 150))

        # set fonts
        self.font = pygame.font.SysFont(None, 80)
        self.small_font = pygame.font.SysFont(None, 40)

        # Hole positions
        self.holes = [(125, 450), (450, 450), (775, 450),
                      (125, 650), (450, 650), (775, 650)]

        self.zombie_frames = {
            "red": self.load_zombie_frames("red"),
            "green": self.load_zombie_frames("green"),
        }

        self.zombies = [
            Zombie(self.zombie_frames["red"], self.holes, self),
            Zombie(self.zombie_frames["green"], self.holes, self)
        ]

        self.occupied_holes = set()

        self.zombies[0].spawn()

        # set state
        self.state = "intro"

    def load_zombie_frames(self, color):
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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if self.state == "intro":
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_button_rect.collidepoint(event.pos):
                        self.state = "play"
                        for z in self.zombies:
                            z.spawn()

    def draw_intro(self):
        self.screen.blit(self.intro_bg, (0, 0))

        title = self.font.render("Whack a Zombie", True, WHITE)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))

        press_start = self.small_font.render("START", True, BLACK)
        self.start_button_rect = pygame.Rect(
            WIDTH//2 - press_start.get_width()//2 - 10,
            400 - 10,
            press_start.get_width() + 20,
            press_start.get_height() + 20
        )

        pygame.draw.rect(self.screen, WHITE, self.start_button_rect, border_radius=20)
        self.screen.blit(press_start, (WIDTH//2 - press_start.get_width()//2, 400))

    def draw_play(self):
        self.screen.blit(self.game_bg, (0, 0))

        # Draw holes
        for pos in self.holes:
            self.screen.blit(self.hole_img, pos)

        # Draw zombies
        for zombie in self.zombies:
            zombie.draw(self.screen)

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self.handle_events()

            if self.state == "intro":
                self.draw_intro()
            elif self.state == "play":
                for zombie in self.zombies:
                    zombie.update(dt)
                self.draw_play()

            pygame.display.update()


if __name__ == "__main__":
    game = WhackAZombie()
    game.run()
