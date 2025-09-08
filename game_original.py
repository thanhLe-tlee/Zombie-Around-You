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
    def __init__(self, frames, holes, game, color):
        self.frames = frames  # {"idle": [...], "dead": [...]}
        self.holes = holes
        self.game = game
        self.color = color

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
                if not self.hit:
                    self.game.misses += 1

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
        self.hammer_img = pygame.image.load("images/hammer.png")
        self.hammer_img = pygame.transform.scale(self.hammer_img, (80, 80))
        self.cursor_visible = True

        # get hammer swing state
        self.hammer_swing = False
        self.hammer_swing_start = 0
        self.hammer_swing_duration = 150

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
            Zombie(self.zombie_frames["red"], self.holes, self, "red"),
            Zombie(self.zombie_frames["green"], self.holes, self, "green")
        ]

        self.occupied_holes = set()


        # set state
        self.state = "intro"

        # score init
        self.score = 0
        self.hits = 0
        self.misses = 0

        # set timer 
        self.time_limit = 60_000 
        self.time_left = self.time_limit
        self.start_time = None

        self.sound_enabled = True


        pygame.mixer.music.load("assets/sound/background-theme.mp3")  # or .wav/.ogg
        pygame.mixer.music.play(-1)  # -1 means loop forever

        # Load boing sound effect
        self.boing_sound = pygame.mixer.Sound("assets/sound/Cartoon Boing.mp3")

    def spawn_wave(self):
        group_size = random.randint(1, 4)
        color = "red" if random.random() < 0.2 else "green"
        z = Zombie(self.zombie_frames[color], self.holes, self, color)

        available = [h for h in self.holes if h not in self.occupied_holes]
        if len(available) < group_size:
            group_size = len(available)

        for _ in range(group_size):
            if not available:
                break
            pos = random.choice(available)
            available.remove(pos)

            color = "red" if random.random() < 0.2 else "green"
            z = Zombie(self.zombie_frames[color], self.holes, self, color)
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

            if event.type == KEYDOWN and event.key == K_p:
                if self.state == "play":
                    self.state = "pause"
                    self.time_left = self.time_limit - (pygame.time.get_ticks() - self.start_time)
                elif self.state == "pause":
                    self.start_time = pygame.time.get_ticks() - (self.time_limit - self.time_left)
                    self.state = "play"

            if event.type == KEYDOWN and event.key == K_m:
                if self.sound_enabled:
                    pygame.mixer.music.pause()
                    self.sound_enabled = False
                else:
                    pygame.mixer.music.unpause()
                    self.sound_enabled = True



            if self.state == "intro":
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_button_rect.collidepoint(event.pos):
                        self.state = "play"
                        self.start_time = pygame.time.get_ticks()
                        self.time_left = self.time_limit
                        for z in self.zombies:
                            z.spawn()

            elif self.state == "play":
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.hammer_swing = True
                    self.hammer_swing_start = pygame.time.get_ticks()
                    for zombie in self.zombies:
                        if zombie.check_hit(event.pos):
                            self.boing_sound.play()
                            if zombie.color == "red":
                                self.score += 2
                            else:
                                self.score += 1
                            self.hits += 1
                            break

            elif self.state == "pause":
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if self.continue_button_rect.collidepoint(event.pos):
                        # Resume
                        self.start_time = pygame.time.get_ticks() - (self.time_limit - self.time_left)
                        self.state = "play"
                    elif self.intro_button_rect.collidepoint(event.pos):
                        # Reset về intro
                        self.score = 0
                        self.hits = 0
                        self.misses = 0
                        self.zombies.clear()
                        self.occupied_holes.clear()
                        self.state = "intro"


            elif self.state == "timesup":
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if self.play_again_rect.collidepoint(event.pos):
                        self.score = 0
                        self.hits = 0
                        self.misses = 0
                        self.zombies.clear()
                        self.occupied_holes.clear()
                        self.start_time = pygame.time.get_ticks()
                        self.time_left = self.time_limit
                        self.state = "play"
                    elif self.intro_button_rect.collidepoint(event.pos):
                        self.score = 0
                        self.hits = 0
                        self.misses = 0
                        self.zombies.clear()
                        self.occupied_holes.clear()
                        self.state = "intro"

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
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 0))
        self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

        hits_text = self.small_font.render(f"Hits: {self.hits}", True, (0, 255, 0))
        misses_text = self.small_font.render(f"Misses: {self.misses}", True, (255, 0, 0))

        if self.hits + self.misses > 0:
            accuracy = (self.hits / (self.hits + self.misses)) * 100
        else:
            accuracy = 0
        accuracy_text = self.small_font.render(f"Accuracy: {accuracy:.1f}%", True, (255, 255, 255))

        self.screen.blit(hits_text, (20, 20))
        self.screen.blit(misses_text, (20, 60))
        self.screen.blit(accuracy_text, (20, 100))

        seconds_left = self.time_left // 1000
        time_text = self.small_font.render(f"Time: {seconds_left}", True, (255, 255, 255))
        self.screen.blit(time_text, (WIDTH - time_text.get_width() - 20, 20))

        sound_text = self.small_font.render(
        "Music: ON" if self.sound_enabled else "Music: OFF", True, (255, 255, 255))
        self.screen.blit(sound_text, (WIDTH - sound_text.get_width() - 20, 60))

        # Draw hammer cursor if mouse is inside window
        if not self.cursor_visible:
            pygame.mouse.set_visible(False)
            mx, my = pygame.mouse.get_pos()
            hammer_img = self.hammer_img
            
            if self.hammer_swing:
                elapsed = pygame.time.get_ticks() - self.hammer_swing_start
                if elapsed < self.hammer_swing_duration:
                    progress = elapsed / self.hammer_swing_duration
                    angle = 45 * (1 - progress)  
                    hammer_img = pygame.transform.rotate(self.hammer_img, angle)
                else:
                    self.hammer_swing = False
                    hammer_img = self.hammer_img
            else:
                hammer_img = self.hammer_img

            
            self.screen.blit(hammer_img, (mx - 40, my - 10))

    def draw_timesup(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("TIME'S UP!", True, (255, 0, 0))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        stats = [
            f"Score: {self.score}",
            f"Hits: {self.hits}",
            f"Misses: {self.misses}",
        ]
        if self.hits + self.misses > 0:
            accuracy = (self.hits / (self.hits + self.misses)) * 100
        else:
            accuracy = 0
        stats.append(f"Accuracy: {accuracy:.1f}%")

        for i, text in enumerate(stats):
            line = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(line, (WIDTH//2 - line.get_width()//2, 250 + i*50))

        # Buttons
        play_again_text = self.small_font.render("Play Again", True, BLACK)
        intro_text = self.small_font.render("Go Back", True, BLACK)

        self.play_again_rect = pygame.Rect(WIDTH//2 - 150, 450, 300, 50)
        self.intro_button_rect = pygame.Rect(WIDTH//2 - 150, 520, 300, 50)

        pygame.draw.rect(self.screen, WHITE, self.play_again_rect, border_radius=15)
        pygame.draw.rect(self.screen, WHITE, self.intro_button_rect, border_radius=15)

        self.screen.blit(play_again_text, (WIDTH//2 - play_again_text.get_width()//2, 460))
        self.screen.blit(intro_text, (WIDTH//2 - intro_text.get_width()//2, 530))

    def draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("PAUSED", True, (255, 255, 0))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))

        continue_text = self.small_font.render("Continue", True, BLACK)
        intro_text = self.small_font.render("Go Back", True, BLACK)

        self.continue_button_rect = pygame.Rect(WIDTH//2 - 150, 350, 300, 50)
        self.intro_button_rect = pygame.Rect(WIDTH//2 - 150, 420, 300, 50)

        pygame.draw.rect(self.screen, WHITE, self.continue_button_rect, border_radius=15)
        pygame.draw.rect(self.screen, WHITE, self.intro_button_rect, border_radius=15)

        self.screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, 360))
        self.screen.blit(intro_text, (WIDTH//2 - intro_text.get_width()//2, 430))


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

            if self.state == "intro":
                pygame.mouse.set_visible(True)
                self.cursor_visible = True
                self.draw_intro()
            elif self.state == "play":
                pygame.mouse.set_visible(False) 
                self.cursor_visible = False
                elapsed = pygame.time.get_ticks() - self.start_time
                self.time_left = max(0, self.time_limit - elapsed)
                if self.time_left == 0:
                    self.state = "timesup"
                for zombie in self.zombies:
                    zombie.update(dt)
                self.zombies = [z for z in self.zombies if z.active or z.rising or z.falling]

                spawn_timer += dt
                if spawn_timer >= spawn_interval:
                    self.spawn_wave()
                    spawn_timer = 0
                self.draw_play()
            elif self.state == "timesup":
                pygame.mouse.set_visible(True) 
                self.cursor_visible = True
                self.draw_timesup()
            elif self.state == "pause":
                pygame.mouse.set_visible(True)
                self.cursor_visible = True
                self.screen.blit(self.game_bg, (0, 0)) 
                self.draw_pause()

            pygame.display.update()


if __name__ == "__main__":
    game = WhackAZombie()
    game.run()
