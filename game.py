import pygame, sys
from pygame.locals import *

pygame.init()
WIDTH, HEIGHT = 1100, 800
DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT)) 

clock = pygame.time.Clock()

pygame.display.set_caption('Whack a Zombie')

# Create intro background for game
intro_background = pygame.image.load('images/intro_bg.jpg')
intro_background = pygame.transform.scale(intro_background, (WIDTH, HEIGHT))

# Create background for game
background = pygame.image.load('images/background.jpg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Create hole for game
hole = pygame.image.load('images/hole.png')
hole = pygame.transform.scale(hole, (200, 150))

# Make holes position
holes = [(125, 450), (450, 450), (775, 450), (125, 650), (450, 650), (775, 650)]

font = pygame.font.SysFont('', 80)
small_font = pygame.font.SysFont('', 40)

state = 'intro'

while True:
    for event in pygame.event.get(): 
        if state == 'intro':
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and event.pos[0] in range(WIDTH//2 - press_start.get_width()//2 - 10, WIDTH//2 + press_start.get_width()//2 + 10) and event.pos[1] in range(400 - 10, 400 + press_start.get_height() + 10):
                    state = 'play'
        
        if event.type == QUIT: 
            pygame.quit() 
            sys.exit() 

    if state == 'intro':
        DISPLAYSURF.blit(intro_background, (0, 0))
        title = font.render('Whack a Zombie', True, (255, 255, 255))
        DISPLAYSURF.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        press_start = small_font.render("START", True, (0, 0, 0))
        pygame.draw.rect(DISPLAYSURF, (255, 255, 255), (WIDTH//2 - press_start.get_width()//2 - 10, 400 - 10, press_start.get_width() + 20, press_start.get_height() + 20), border_radius = 20)
        DISPLAYSURF.blit(press_start, (WIDTH//2 - press_start.get_width()//2, 400))
    elif state == 'play':
        DISPLAYSURF.blit(background, (0, 0))
        for pos in holes:
            DISPLAYSURF.blit(hole, pos)
    
    pygame.display.update()
    clock.tick(60)
