def titlescreen():
    """ this is for the user to prepare for the game after the user gives the input enter to continue or q to exit """

    # texture for background of titlescreen
    background = pygame.image.load("titlescreen.png")

    # text telling the user what they can do
    font = pygame.font.SysFont('Arial', 50)
    text = font.render('press enter to play or press q to exit', True, (0, 125, 0))
    # textbox where the text goes
    textbox = text.get_rect()
    textbox.center = (500, 500)

    # loop waiting for the user to press enter or q
    waiting = True
    while waiting:
        # this checks if the user has pressed either button
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    # this closes the game
                    sys.exit()
                if event.key == pygame.K_RETURN:
                    # this exits the loop after this iteration is complete
                    waiting = False

        # this adds the background and textbox to the display then updates it
        screen.blit(background, (0, 0))
        screen.blit(text, textbox)
        pygame.display.update()

        # simple delay that likely wont bother users when they choose what to do
        time.sleep(1)


# imports libraries
import sys
import time
import pygame

# starts pygame modules
pygame.init()
# starts playing the background music
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.play(-1, 0.0)

# the display for the game, i decided to make it a global variable since anything that needs to be displayed will change it
global screen
screen = pygame.display.set_mode((1000, 1000), pygame.FULLSCREEN)

# displays the game's titlescreen
titlescreen()

# variables for use in game
background = pygame.image.load("field.png")       # background for game
normal_tile_colour = (164, 83, 38)                # colour of tiles when not touching mouse
touching_mouse_tile_colour = (204, 124, 38)       # colour of tiles when touching mouse
inhand = 0                                        # what is the user holding (currently just used for seedpack)
SeedPack = pygame.image.load("CropSeed.png")      # texture for seedpack for generic crop
SeededTexture = pygame.image.load("Planted.png")  # Texture for tiles with seeds
seeded = []                                       # whether the tiles have seeds or not
for looper in range(4):
    seeded.append([])
    for looper2 in range(8):
        seeded[looper].append(0)

while True:
    """main game loop"""

    # checks if the user has pressed q
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                sys.exit()

    # displays the background for the field
    screen.blit(background, (0, 0))

    # gets mouse location
    (mousex, mousey) = pygame.mouse.get_pos()

    # creates the tiles of the field
    y = 0
    while y < 4:
        # y position of tile
        # every iteration the tiles are placed 150 pixels down from the previous iteration of tiles
        tiley = 500 + 130 * y

        x = 0
        while x < 8:
            # x position of tile
            # every iteration the tile is placed 150 pixels right from the previous one
            tilex = 230 + 130 * x

            # tile appearence to display
            tile = pygame.Rect(tilex, tiley, 100, 100)

            # check if tile is touching mouse, if it is use the brighter colour
            if (tilex < mousex < tilex + 100) and (tiley < mousey < tiley + 100):
                pygame.draw.rect(screen, touching_mouse_tile_colour, tile)
                if pygame.mouse.get_pressed()[0] and inhand == 1:
                    seeded[y][x] = 1
            else:
                pygame.draw.rect(screen, normal_tile_colour, tile)
            
            if seeded[y][x] == 1:
                screen.blit(SeededTexture, (tilex, tiley))

            # next iteration of inner loop
            x += 1
        
        # next iteration of outer loop
        y += 1
    
    # user equip seedpack
    if pygame.mouse.get_pressed()[0] and (50 < mousex < 50 + 107) and (500 < mousey < 500 + 135):
        if inhand == 1:
            inhand = 0
        else:
            inhand = 1

    # seedpack placement
    if inhand == 1:
        screen.blit(SeedPack, (mousex, mousey))
    else:
        screen.blit(SeedPack, (50, 500))

    # updates the display and a small delay so that the game mechanics dont go so fast
    pygame.display.update()
    time.sleep(0.05)
