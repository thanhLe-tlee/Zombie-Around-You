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

        # For got-hit/fade-out
        self.hit = False
        self.alpha = 255
        self.fade_speed = 10  # alpha decrease per frame when hit

    def reset(self):
        self.active = False
        self.rect.topleft = (-200, 200)
        self.hit = False
        self.alpha = 255
        self.state = "idle"
        self.frame_index = 0
        self.image = self.frames[self.state][self.frame_index]

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

        # Reset hit/fade state and animation
        self.hit = False
        self.alpha = 255
        self.state = "idle"
        self.frame_index = 0
        self.image = self.frames[self.state][self.frame_index]

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

        if self.hit:
            # Fade out
            self.alpha -= self.fade_speed
            if self.alpha <= 0:
                self.alpha = 0
                self.active = False
                self.hit = False
                if hasattr(self, "current_hole"):
                    self.game.occupied_holes.discard(self.current_hole)
            return

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
            img = self.image.copy()
            if self.hit:
                img.set_alpha(self.alpha)
            screen.blit(img, self.rect)

    def check_hit(self, pos):
        if self.active and not self.hit and self.rect.collidepoint(pos):
            self.state = "dead"
            self.frame_index = 0
            self.hit = True
            self.alpha = 255
            return True
        return False


class WhackAZombie:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Whack a Zombie")
        self.clock = pygame.time.Clock()

    # Load assets
        self.intro_bg = pygame.transform.scale(pygame.image.load("images/intro_bg.jpg"), (WIDTH, HEIGHT))
        self.game_bg = pygame.transform.scale(pygame.image.load("images/background.jpg"), (WIDTH, HEIGHT))
        self.hole_img = pygame.transform.scale(pygame.image.load("images/hole.png"), (200, 150))

        # Load hammer image for custom cursor
        self.hammer_img = pygame.image.load("images/hammer.jpg")
        self.hammer_img = pygame.transform.scale(self.hammer_img, (80, 80))
        self.cursor_visible = True

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


        # set state
        self.state = "intro"

        # Hammer and health variables
        self.hammer_duration = 20
        self.hammer_duration_max = 20
        self.health_condition = 5
        self.health_condition_max = 5
        self.last_health_tick = pygame.time.get_ticks()

        pygame.mixer.music.load("assets/sound/background-theme.mp3")  # or .wav/.ogg
        pygame.mixer.music.play(-1)  # -1 means loop forever

        # Load boing sound effect
        self.boing_sound = pygame.mixer.Sound("assets/sound/Cartoon Boing.mp3")

    def spawn_wave(self):
        group_size = random.randint(1, 4)
        available = [h for h in self.holes if h not in self.occupied_holes]
        if len(available) < group_size:
            group_size = len(available)

        for _ in range(group_size):
            if not available:
                break
            pos = random.choice(available)
            available.remove(pos)

            color = "red" if random.random() < 0.2 else "green"
            z = Zombie(self.zombie_frames[color], self.holes, self)
            z.rect.midbottom = (pos[0] + 100, pos[1] + 120)
            z.base_y = z.rect.bottom
            z.target_y = z.base_y - 40
            z.rising = True
            z.active = True
            z.current_hole = pos
            self.occupied_holes.add(pos)
            self.zombies.append(z)

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

            if event.type == ACTIVEEVENT:
                # Window focus or mouse enter/leave
                if hasattr(event, 'gain') and hasattr(event, 'state'):
                    if event.state == 2:  # 2 = mouse focus
                        if event.gain == 1:
                            pygame.mouse.set_visible(True)
                            self.cursor_visible = False
                        else:
                            pygame.mouse.set_visible(True)
                            self.cursor_visible = True

            if self.state == "intro":
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_button_rect.collidepoint(event.pos):
                        self.state = "play"
                        for z in self.zombies:
                            z.spawn()
            elif self.state == "play":
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    # Only allow hit if hammer duration > 0
                    if self.hammer_duration > 0:
                        # Reduce hammer duration by 2 on every click
                        if self.hammer_duration > 2:
                            self.hammer_duration -= 5
                        else:
                            self.hammer_duration = 0
                        # Try to hit a zombie
                        for zombie in self.zombies:
                            if zombie.check_hit(event.pos):
                                self.boing_sound.play()
                                # Only increase if not at max and hammer_duration > 0
                                if self.hammer_duration < self.hammer_duration_max:
                                    self.hammer_duration = min(self.hammer_duration + 6, self.hammer_duration_max)
                                # Only increase health if not at max
                                if self.health_condition < self.health_condition_max:
                                    self.health_condition = min(self.health_condition + 1, self.health_condition_max)
                                break  # Only hit one zombie per click

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

        # Display hammer duration and health condition
        hammer_text = self.small_font.render(f"Hammer: {self.hammer_duration}/{self.hammer_duration_max}", True, (255,255,0))
        health_text = self.small_font.render(f"Health: {self.health_condition}/{self.health_condition_max}", True, (0,255,0))
        self.screen.blit(hammer_text, (20, 20))
        self.screen.blit(health_text, (20, 60))

        # Draw hammer cursor if mouse is inside window
        if not self.cursor_visible:
            pygame.mouse.set_visible(False)
            mx, my = pygame.mouse.get_pos()
            # Offset so hammer tip is at mouse
            self.screen.blit(self.hammer_img, (mx - 40, my - 10))

    def run(self):
        spawn_timer = 0
        spawn_interval = 2000

        # Hide system cursor at start if mouse is inside window
        if pygame.mouse.get_focused() and self:
            pygame.mouse.set_visible(False)
            self.cursor_visible = False
        else:
            pygame.mouse.set_visible(True)
            self.cursor_visible = True

        while True:
            dt = self.clock.tick(FPS)
            self.handle_events()

            # Decrease health_condition by 1 every second
            now = pygame.time.get_ticks()
            if self.state == "play" and now - self.last_health_tick >= 1000:
                if self.health_condition > 0:
                    self.health_condition -= 1
                self.last_health_tick = now

            if self.state == "intro":
                self.draw_intro()
            elif self.state == "play":
                for zombie in self.zombies:
                    zombie.update(dt)
                self.zombies = [z for z in self.zombies if z.active or z.rising or z.falling]

                spawn_timer += dt
                if spawn_timer >= spawn_interval:
                    self.spawn_wave()
                    spawn_timer = 0
                self.draw_play()

            pygame.display.update()


if __name__ == "__main__":
    game = WhackAZombie()
    game.run()
