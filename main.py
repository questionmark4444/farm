def titlescreen():
    """ this is for the user to prepare for the game after the user gives the input enter to continue or q to exit """

    # amount of frames in the recording
    image_frames = 0

    # texture for background of titlescreen
    background = pygame.image.load("titlescreen.png")

    # text telling the user what they can do
    font = pygame.font.SysFont('Arial', 50)
    text = font.render('press enter to play or press q to exit', True, (0, 125, 0))
    # textbox where the text goes
    textbox = text.get_rect()
    textbox.center = (500, 500)

    # create screenshots folder
    os.makedirs("./recording")
    
    # loop waiting for the user to press enter or q
    waiting = True
    while waiting:
        # this checks if the user has pressed either button
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    # this closes the game
                    exit_game(image_frames)
                if event.key == pygame.K_RETURN:
                    # this exits the loop after this iteration is complete
                    waiting = False

        # this adds the background and textbox to the display then updates it
        screen.blit(background, (0, 0))
        screen.blit(text, textbox)
        pygame.display.update()

        # takes frame then saves to folder to use less ram
        image_frames += 1
        pygame.image.save(screen, f"recording/frame{image_frames}.png")
        # for resizing frames that are not 1000 by 1000
        resize_image = pygame.image.load(f"recording/frame{image_frames}.png")
        resize_image = pygame.transform.scale(resize_image, (1000, 1000))
        pygame.image.save(resize_image, f"recording/frame{image_frames}.png")

        # simple delay that likely wont bother users when they choose what to do
        time.sleep(1)

    # return the beginning of the recording which was on the titlescreen
    return image_frames

# exits the game, i made this a separate function because of the complexity the recorder adds
def exit_game(image_frames):
    # length of final video
    video_length = image_frames/5
    # create list of file paths of each frame
    image_path = []
    frame = 1
    while frame <= image_frames:
        image_path.append(f"recording/frame{frame}.png")
        frame += 1
    # convert frames into 5 frame per second video
    images_to_video(image_path, "merge.mp4", 5)
    # add background music to video
    combine_audio("merge.mp4", "music.mp3", "uncut.mp4", 5)
    # when the music is longer than the recording it extends the last frame, 
    # this trims the video to soundless length to fix that
    # unfortunately if the recording is longer than the music it will not loop
    # i will fix this later in the other tests
    cutter("uncut.mp4", 0, video_length, targetname="recording.mp4")
    # deletes intermidiate processing files
    os.remove("merge.mp4")
    os.remove("uncut.mp4")
    for path in image_path:
        os.remove(path)
    os.rmdir("recording")
    # exits
    sys.exit()

def images_to_video(frame_paths, output_path, fps):
    """this converts the frames into a video for recording"""

    # Create the video from the paths
    video = video_converter.ImageSequenceClip(frame_paths, fps=fps)

    # output the video
    video.write_videofile(output_path)

def combine_audio(video_name, audio_name, output_name, fps):
    """combine video with audio"""
    video = media_getter.VideoFileClip(video_name)
    audio = media_getter.AudioFileClip(audio_name)
    final_video = video.set_audio(audio)
    final_video.write_videofile(output_name,fps=fps)

# imports libraries
import sys
import time
import pygame
import cv2
import os
import moviepy.editor as media_getter
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip as cutter
import moviepy.video.io.ImageSequenceClip as video_converter

# starts pygame modules
pygame.init()

# starts playing the background music
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.play(-1, 0.0)

# the display for the game, i decided to make it a global variable since anything that needs to be displayed will change it
global screen
screen = pygame.display.set_mode((1000, 1000), pygame.FULLSCREEN)

# displays the game's titlescreen and gets image frames
image_frames = titlescreen()

# variables for use in game
background = pygame.image.load("field.png")                        # background for game
normal_tile_colour = (164, 83, 38)                                 # colour of tiles when not touching mouse
touching_mouse_tile_colour = (204, 124, 38)                        # colour of tiles when touching mouse
inhand = 0                                                         # what is the user holding (currently just used for seedpack)
crop = 0                                                           # amount of crop harvested
SeedPack = pygame.image.load("CropSeed.png")                       # texture for seedpack for generic crop
SeededTexture = pygame.image.load("Planted.png")                   # Texture for tiles with seeds
WateringCan = pygame.image.load("WateringCan.png")                 # texture for watering can
WateredSeededTexture = pygame.image.load("WateredSeeds.png")       # Texture for tiles with watered seeds
SeedlingTexture = pygame.image.load("seedlings.png")               # Texture for tiles with seedlings
WateredSeedlingTexture = pygame.image.load("WateredSeedlings.png") # Texture for tiles with watered seedlings
FullyGrownTexture = pygame.image.load("FullyGrown.png")            # Texture for tiles with fully grown crops
Scyth = pygame.image.load("scyth.png")                             # Texture for scyth

seeded = []                                                        # whether the tiles have seeds or not
for looper in range(4):
    seeded.append([])                                              # adding individually because multiplication causes the collums to be syncronised
    for looper2 in range(8):
        seeded[looper].append(0)                                   # state of growth
        seeded[looper].append(0)                                   # timer

font = pygame.font.Font('freesansbold.ttf', 32)                    # font for harvest text
text = font.render(f'amount of crop: {crop}', True, (0, 255, 0))   # this is for setting up textRect it will be changed later
textRect = text.get_rect()                                         # this is the text box
textRect.center = (150, 20)                                        # set textbox location

while True:
    """main game loop"""

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            # checks if the user has pressed q and exits the game if they did
            if event.key == pygame.K_q:
                exit_game(image_frames)
            # checks if the user has pressed p and screenshots if they did
            if event.key == pygame.K_p:
                pygame.image.save(screen, "screenshot.png")

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
                # display tile as brighter colour to signify that the game recognizes that the mouse is touching it
                pygame.draw.rect(screen, touching_mouse_tile_colour, tile)

                # using 2 multiplied by x since the tiles are now 2 values with the odd numbered list parts being timers
                # plant seeds
                if pygame.mouse.get_pressed()[0] and inhand == 1 and seeded[y][2 * x] == 0:
                    seeded[y][2 * x] = 1
                # triggered by clicking a tile with a watering can
                if pygame.mouse.get_pressed()[0] and inhand == 2:
                    # water seeds and start timer
                    if seeded[y][2 * x] == 1:
                        seeded[y][2 * x] = 2
                        seeded[y][2 * x + 1] = time.time()
                    # water seedlings and start timer
                    if seeded[y][2 * x] == 3:
                        seeded[y][2 * x] = 4
                        seeded[y][2 * x + 1] = time.time()
                # harvest fully grown crop with scyth
                if pygame.mouse.get_pressed()[0] and inhand == 3 and seeded[y][2 * x] == 5:
                    seeded[y][2 * x] = 0
                    crop += 10
            else:
                # display normal tile colour
                pygame.draw.rect(screen, normal_tile_colour, tile)

            # if the tile has seeds
            if seeded[y][2 * x] == 1:
                # display the seeds' texture
                screen.blit(SeededTexture, (tilex, tiley))
                # if the timer is not 0 meaning it was watered
                if seeded[y][2 * x + 1] != 0:
                    # if it has been 2 minutes since it became less wet convert it to seedling
                    if time.time() - seeded[y][2 * x + 1] > 120:
                        seeded[y][2 * x] = 3
                        seeded[y][2 * x + 1] = 0

            # if the tile has watered seeds
            if seeded[y][2 * x] == 2:
                # display the watered seeds' texture
                screen.blit(WateredSeededTexture, (tilex, tiley))
                # if it has been at least a minute since it has been watered then convert it back to unwatered seeds but with timer for growth
                if time.time() - seeded[y][2 * x + 1] > 60:
                    seeded[y][2 * x] = 1
                    seeded[y][2 * x + 1] = time.time()

            # if the tile has seedlings
            if seeded[y][2 * x] == 3:
                # display the seedlings' texture
                screen.blit(SeedlingTexture, (tilex, tiley))
                # if the timer is not 0 meaning it was watered
                if seeded[y][2 * x + 1] != 0:
                    # if it has been 2 minutes since it became less wet convert it to fully grown crop
                    if time.time() - seeded[y][2 * x + 1] > 120:
                        seeded[y][2 * x] = 5
                        seeded[y][2 * x + 1] = 0

            # if the tile has watered seedlings
            if seeded[y][2 * x] == 4:
                # display the watered seedlings' texture
                screen.blit(WateredSeedlingTexture, (tilex, tiley))
                # if it has been at least a minute since it has been watered then convert it back to unwatered seedlings but with timer for growth
                if time.time() - seeded[y][2 * x + 1] > 60:
                    seeded[y][2 * x] = 3
                    seeded[y][2 * x + 1] = time.time()

            # if the tile has fully grown crops
            if seeded[y][2 * x] == 5:
                # display the fully grown crops' texture
                screen.blit(FullyGrownTexture, (tilex, tiley))

            # next iteration of inner loop
            x += 1
        
        # next iteration of outer loop
        y += 1
    
    # user equip seedpack
    if pygame.mouse.get_pressed()[0] and (50 < mousex < 157) and (500 < mousey < 635):
        # check if the user was already holding an item and put it away otherwise equip the seedpack
        if inhand != 0:
            inhand = 0
        else:
            inhand = 1

    # check if the user is holding the seedpack
    if inhand == 1:
        # put it where the mouse it
        screen.blit(SeedPack, (mousex, mousey))
    else:
        # put the seedpack in its place in the toolbar
        screen.blit(SeedPack, (50, 500))

    # user equip watering can
    if pygame.mouse.get_pressed()[0] and (50 < mousex < 157) and (660 < mousey < 795):
        # check if the user was already holding an item and put it away otherwise equip the watering can
        if inhand != 0:
            inhand = 0
        else:
            inhand = 2

    # check if the user is holding the watering can
    if inhand == 2:
        # put it where the mouse it
        screen.blit(WateringCan, (mousex, mousey))
    else:
        # put the watering can in its place in the toolbar
        screen.blit(WateringCan, (50, 660))

    # user equip scyth
    if pygame.mouse.get_pressed()[0] and (50 < mousex < 157) and (820 < mousey < 795 * 2 + 635):
        # check if the user was already holding an item and put it away otherwise equip the scyth
        if inhand != 0:
            inhand = 0
        else:
            inhand = 3

    # check if the user is holding the scyth
    if inhand == 3:
        # put it where the mouse it
        screen.blit(Scyth, (mousex, mousey))
    else:
        # put the scyth in its place in the toolbar
        screen.blit(Scyth, (50, 820))

    # this updates the text for any harvested crops
    text = font.render(f'amount of crop: {crop}', True, (0, 100, 0))
    # this uses the inital textbox for the new text
    screen.blit(text, textRect)

    # takes frame then saves to folder to use less ram
    image_frames += 1
    pygame.image.save(screen, f"recording/frame{image_frames}.png")
    # for resizing frames that are not 1000 by 1000
    resize_image = pygame.image.load(f"recording/frame{image_frames}.png")
    resize_image = pygame.transform.scale(resize_image, (1000, 1000))
    pygame.image.save(resize_image, f"recording/frame{image_frames}.png")

    # updates the display and a small delay so that the game mechanics dont go so fast
    pygame.display.update()
    time.sleep(0.05)
