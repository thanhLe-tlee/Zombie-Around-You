import pygame
import random

class Zombie:
    def __init__(self, frames, holes, game_state, color):
        self.frames = frames  # {"idle": [...], "dead": [...]}
        self.holes = holes
        self.game_state = game_state  
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
        available = [h for h in self.holes if h not in self.game_state.occupied_holes]
        if not available:
            return
        self.active = True
        pos = random.choice(available)
        self.rect.midbottom = (pos[0] + 100, pos[1] + 120)

        self.current_hole = pos
        self.game_state.occupied_holes.add(pos)

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
                    self.game_state.occupied_holes.discard(self.current_hole)
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
                    self.game_state.occupied_holes.discard(self.current_hole)
                if not self.hit:
                    self.game_state.misses += 1 # Update game_state.misses

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