import pygame, sys, random
from pygame.locals import *

from constants import WIDTH, HEIGHT, WHITE, BLACK, FPS
from sprites.zombie import Zombie
from game_state import GameState
from ui import GameUI

pygame.init()
pygame.mixer.init()

class WhackAZombie:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Whack a Zombie")
        self.clock = pygame.time.Clock()

        self.game_state = GameState()

        # Load assets
        self.images = {
            'intro_bg': pygame.transform.scale(pygame.image.load("images/intro_bg.jpg"), (WIDTH, HEIGHT)),
            'game_bg': pygame.transform.scale(pygame.image.load("images/background.jpg"), (WIDTH, HEIGHT)),
            'hole': pygame.transform.scale(pygame.image.load("images/hole.png"), (200, 150)),
            'hammer': pygame.transform.scale(pygame.image.load("images/hammer.png"), (80, 80))
        }

        # Fonts
        self.fonts = {
            'large': pygame.font.SysFont(None, 80),
            'small': pygame.font.SysFont(None, 40)
        }

        self.ui = GameUI(self.screen, self.fonts, self.images)

        # Hammer state for UI
        self.hammer_state = {
            'hammer_swing': False,
            'hammer_swing_start': 0,
            'hammer_swing_duration': 150,
            'cursor_visible': True # Initial state, will be set by run loop
        }

        # Hole positions
        self.holes = [(125, 450), (450, 450), (775, 450),
                      (125, 650), (450, 650), (775, 650)]

        self.zombie_frames = {
            "red": self.load_zombie_frames("red"),
            "green": self.load_zombie_frames("green"),
        }

        self.zombies = [] # Zombies will be spawned dynamically

        pygame.mixer.music.load("assets/sound/background-theme.mp3")
        pygame.mixer.music.play(-1)
        self.boing_sound = pygame.mixer.Sound("assets/sound/Cartoon Boing.mp3")

    def spawn_wave(self):
        group_size = random.randint(1, 4)
        available = [h for h in self.holes if h not in self.game_state.occupied_holes]
        if len(available) < group_size:
            group_size = len(available)

        # Reuse existing zombies if possible
        inactive_zombies = [z for z in self.zombies if not z.active]

        # Spawn new zombies if not enough inactive zombies
        while len(inactive_zombies) < group_size:
            color = "red" if random.random() < 0.2 else "green"
            z = Zombie(self.zombie_frames[color], self.holes, self.game_state, color)
            self.zombies.append(z)
            inactive_zombies.append(z)

        for _ in range(group_size):
            if not available:
                break
            pos = random.choice(available)
            available.remove(pos)

            zombie = inactive_zombies.pop(0)
            zombie.spawn()  # Use spawn method to set position and state
            zombie.rect.midbottom = (pos[0] + 100, pos[1] + 120)
            zombie.base_y = zombie.rect.bottom
            zombie.target_y = zombie.base_y - 40
            zombie.rising = True
            zombie.active = True
            zombie.current_hole = pos
            self.game_state.occupied_holes.add(pos)

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

            if event.type == KEYDOWN and event.key == K_p:
                if self.game_state.state == "play":
                    self.game_state.state = "pause"
                    self.game_state.time_left = self.game_state.time_limit - (pygame.time.get_ticks() - self.game_state.start_time)
                elif self.game_state.state == "pause":
                    self.game_state.start_time = pygame.time.get_ticks() - (self.game_state.time_limit - self.game_state.time_left)
                    self.game_state.state = "play"

            if event.type == KEYDOWN and event.key == K_m:
                if self.game_state.sound_enabled:
                    pygame.mixer.music.pause()
                    self.game_state.sound_enabled = False
                else:
                    pygame.mixer.music.unpause()
                    self.game_state.sound_enabled = True

            button_rects = self.ui.get_button_rects()

            if self.game_state.state == "intro":
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if 'start' in button_rects and button_rects['start'].collidepoint(event.pos):
                        self.game_state.state = "play"
                        self.game_state.start_time = pygame.time.get_ticks()
                        self.game_state.time_left = self.game_state.time_limit

            elif self.game_state.state == "play":
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.hammer_state['hammer_swing'] = True
                    self.hammer_state['hammer_swing_start'] = pygame.time.get_ticks()
                    for zombie in self.zombies:
                        if zombie.check_hit(event.pos):
                            self.boing_sound.play()
                            if zombie.color == "red":
                                self.game_state.score += 2
                            else:
                                self.game_state.score += 1
                            self.game_state.hits += 1
                            break

            elif self.game_state.state == "pause":
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if 'continue' in button_rects and button_rects['continue'].collidepoint(event.pos):
                        # Resume
                        self.game_state.start_time = pygame.time.get_ticks() - (self.game_state.time_limit - self.game_state.time_left)
                        self.game_state.state = "play"
                    elif 'pause_intro' in button_rects and button_rects['pause_intro'].collidepoint(event.pos):
                        # Reset to intro
                        self.game_state.reset()
                        self.zombies.clear()
                        self.game_state.occupied_holes.clear()
                        self.game_state.state = "intro"

            elif self.game_state.state == "timesup":
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if 'play_again' in button_rects and button_rects['play_again'].collidepoint(event.pos):
                        self.game_state.reset()
                        self.zombies.clear()
                        self.game_state.occupied_holes.clear()
                        self.game_state.start_time = pygame.time.get_ticks()
                        self.game_state.time_left = self.game_state.time_limit
                        self.game_state.state = "play"
                        self.spawn_wave() # Spawn new zombies for new game
                    elif 'intro' in button_rects and button_rects['intro'].collidepoint(event.pos):
                        self.game_state.reset()
                        self.zombies.clear()
                        self.game_state.occupied_holes.clear()
                        self.game_state.state = "intro"

    def run(self):
        spawn_timer = 0
        spawn_interval = 2000

        # Hide system cursor at start if mouse is inside window
        if pygame.mouse.get_focused():
            pygame.mouse.set_visible(False)
            self.hammer_state['cursor_visible'] = False
        else:
            pygame.mouse.set_visible(True)
            self.hammer_state['cursor_visible'] = True

        while True:
            dt = self.clock.tick(FPS)
            self.handle_events()

            if self.game_state.state == "intro":
                pygame.mouse.set_visible(True)
                self.hammer_state['cursor_visible'] = True
                self.ui.draw_intro()
            elif self.game_state.state == "play":
                pygame.mouse.set_visible(False) 
                self.hammer_state['cursor_visible'] = False
                
                elapsed = pygame.time.get_ticks() - self.game_state.start_time
                self.game_state.time_left = max(0, self.game_state.time_limit - elapsed)
                
                if self.game_state.time_left == 0:
                    self.game_state.state = "timesup"
                
                for zombie in self.zombies:
                    zombie.update(dt)
                # Filter out inactive zombies and update occupied_holes
                self.zombies = [z for z in self.zombies if z.active or z.rising or z.falling]
                self.game_state.occupied_holes = {z.current_hole for z in self.zombies if hasattr(z, 'current_hole') and z.active}


                spawn_timer += dt
                if spawn_timer >= spawn_interval:
                    self.spawn_wave()
                    spawn_timer = 0
                
                self.ui.draw_play(self.game_state, self.holes, self.zombies, self.hammer_state)
            elif self.game_state.state == "timesup":
                pygame.mouse.set_visible(True) 
                self.hammer_state['cursor_visible'] = True
                self.ui.draw_timesup(self.game_state)
            elif self.game_state.state == "pause":
                pygame.mouse.set_visible(True)
                self.hammer_state['cursor_visible'] = True
                self.screen.blit(self.images['game_bg'], (0, 0)) # Draw background under pause overlay
                self.ui.draw_pause()

            pygame.display.update()


if __name__ == "__main__":
    game = WhackAZombie()
    game.run()