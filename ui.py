import pygame
from constants import WIDTH, HEIGHT, WHITE, BLACK

class GameUI:
    def __init__(self, screen, fonts, images):
        self.screen = screen
        self.fonts = fonts
        self.images = images
        self.button_rects = {}

    def draw_intro(self):
        self.screen.blit(self.images['intro_bg'], (0, 0))

        title = self.fonts['large'].render("Whack a Zombie", True, WHITE)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))

        press_start = self.fonts['small'].render("START", True, BLACK)
        self.button_rects['start'] = pygame.Rect(
            WIDTH//2 - press_start.get_width()//2 - 10,
            400 - 10,
            press_start.get_width() + 20,
            press_start.get_height() + 20
        )

        pygame.draw.rect(self.screen, WHITE, self.button_rects['start'], border_radius=20)
        self.screen.blit(press_start, (WIDTH//2 - press_start.get_width()//2, 400))

    def draw_play(self, game_state, holes, zombies, hammer_state):
        self.screen.blit(self.images['game_bg'], (0, 0))

        # Draw holes
        for pos in holes:
            self.screen.blit(self.images['hole'], pos)

        # Draw zombies
        for zombie in zombies:
            zombie.draw(self.screen)

        # Draw score and stats
        score_text = self.fonts['large'].render(f"Score: {game_state.score}", True, (255, 255, 0))
        self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

        hits_text = self.fonts['small'].render(f"Hits: {game_state.hits}", True, (0, 255, 0))
        misses_text = self.fonts['small'].render(f"Misses: {game_state.misses}", True, (255, 0, 0))

        if game_state.hits + game_state.misses > 0:
            accuracy = (game_state.hits / (game_state.hits + game_state.misses)) * 100
        else:
            accuracy = 0
        accuracy_text = self.fonts['small'].render(f"Accuracy: {accuracy:.1f}%", True, WHITE)

        self.screen.blit(hits_text, (20, 20))
        self.screen.blit(misses_text, (20, 60))
        self.screen.blit(accuracy_text, (20, 100))

        seconds_left = game_state.time_left // 1000
        time_text = self.fonts['small'].render(f"Time: {seconds_left}", True, WHITE)
        self.screen.blit(time_text, (WIDTH - time_text.get_width() - 20, 20))

        sound_text = self.fonts['small'].render(
            "Music: ON" if game_state.sound_enabled else "Music: OFF", True, WHITE)
        self.screen.blit(sound_text, (WIDTH - sound_text.get_width() - 20, 60))

        # Draw hammer cursor
        if not hammer_state['cursor_visible']:
            pygame.mouse.set_visible(False)
            mx, my = pygame.mouse.get_pos()
            hammer_img = self.images['hammer']
            
            if hammer_state['hammer_swing']:
                elapsed = pygame.time.get_ticks() - hammer_state['hammer_swing_start']
                if elapsed < hammer_state['hammer_swing_duration']:
                    progress = elapsed / hammer_state['hammer_swing_duration']
                    angle = 45 * (1 - progress)
                    hammer_img = pygame.transform.rotate(self.images['hammer'], angle)

            self.screen.blit(hammer_img, (mx - 40, my - 10))

    def draw_timesup(self, game_state):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.fonts['large'].render("TIME'S UP!", True, (255, 0, 0))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        stats = [
            f"Score: {game_state.score}",
            f"Hits: {game_state.hits}",
            f"Misses: {game_state.misses}",
        ]
        if game_state.hits + game_state.misses > 0:
            accuracy = (game_state.hits / (game_state.hits + game_state.misses)) * 100
        else:
            accuracy = 0
        stats.append(f"Accuracy: {accuracy:.1f}%")

        for i, text in enumerate(stats):
            line = self.fonts['small'].render(text, True, WHITE)
            self.screen.blit(line, (WIDTH//2 - line.get_width()//2, 250 + i*50))

        # Buttons
        play_again_text = self.fonts['small'].render("Play Again", True, BLACK)
        intro_text = self.fonts['small'].render("Go Back", True, BLACK)

        self.button_rects['play_again'] = pygame.Rect(WIDTH//2 - 150, 450, 300, 50)
        self.button_rects['intro'] = pygame.Rect(WIDTH//2 - 150, 520, 300, 50)

        pygame.draw.rect(self.screen, WHITE, self.button_rects['play_again'], border_radius=15)
        pygame.draw.rect(self.screen, WHITE, self.button_rects['intro'], border_radius=15)

        self.screen.blit(play_again_text, (WIDTH//2 - play_again_text.get_width()//2, 460))
        self.screen.blit(intro_text, (WIDTH//2 - intro_text.get_width()//2, 530))

    def draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.fonts['large'].render("PAUSED", True, (255, 255, 0))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))

        continue_text = self.fonts['small'].render("Continue", True, BLACK)
        intro_text = self.fonts['small'].render("Go Back", True, BLACK)

        self.button_rects['continue'] = pygame.Rect(WIDTH//2 - 150, 350, 300, 50)
        self.button_rects['pause_intro'] = pygame.Rect(WIDTH//2 - 150, 420, 300, 50)

        pygame.draw.rect(self.screen, WHITE, self.button_rects['continue'], border_radius=15)
        pygame.draw.rect(self.screen, WHITE, self.button_rects['pause_intro'], border_radius=15)

        self.screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, 360))
        self.screen.blit(intro_text, (WIDTH//2 - intro_text.get_width()//2, 430))

    def get_button_rects(self):
        return self.button_rects
