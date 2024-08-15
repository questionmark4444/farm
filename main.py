def titlescreen():
    """ this is for the user to prepare for the game after the user gives the input enter to continue or q to exit """

    # frames of recording
    image_frames = []

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
                    exit_game(image_frames)
                if event.key == pygame.K_RETURN:
                    # this exits the loop after this iteration is complete
                    waiting = False

        # this adds the background and textbox to the display then updates it
        screen.blit(background, (0, 0))
        screen.blit(text, textbox)
        pygame.display.update()

        pygame.image.save(screen, "screenshot.png")
        image_frames.append(cv2.imread("screenshot.png"))

        # simple delay that likely wont bother users when they choose what to do
        time.sleep(1)
    # return the beginning of the recording which was on the titlescreen
    return image_frames

# exits the game, i made this a separate function because of the complexity the recorder adds
def exit_game(image_frames):
    # length of final video
    video_length = len(image_frames)/5
    # convert images into 5 frame per second video
    images_to_video(image_frames, "merge.mp4", 5)
    # add background music to video
    combine_audio("merge.mp4", "music.mp3", "uncut.mp4", 5)
    # the music is longer than the current test so it extends the last frame, \
    # this trims the video to soundless length to fix that
    # unfortunately if the recording is longer than the music it will not loop
    # i will fix this later in the other tests
    cutter("uncut.mp4", 0, video_length, targetname="recording.mp4")
    # deletes intermidiate processing files
    os.remove("screenshot.png")
    os.remove("merge.mp4")
    os.remove("uncut.mp4")
    # exits
    sys.exit()

def images_to_video(image_list, output_path, fps):
    """this converts the images into a video for recording"""

    # Read the first image to get dimensions
    first_image = image_list[0]
    height, width, layers = first_image.shape

    # Create a video writer object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # default mp4 codec doesnt work
    video = cv2.VideoWriter(output_path,      # output path
                        fourcc,           # codec
                        fps,              # frames per second
                        (width, height))  # width and height of video and game

    # Write each image as a frame
    for image in image_list:
        video.write(image)

    # Release the video writer
    video.release()

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

# starts pygame modules
pygame.init()
# starts playing the background music
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.play(-1, 0.0)

# the display for the game, i decided to make it a global variable since anything that needs to be displayed will change it
global screen
screen = pygame.display.set_mode((1000, 1000), pygame.FULLSCREEN)

# this is the tool the user is currently using, (reminder to expand later)
global inhand

# displays the game's titlescreen and gets image frames
image_frames = titlescreen()

# debug
font = pygame.font.SysFont('Arial', 50)
text = font.render('press enter to play or press q to exit', True, (0, 125, 0))
textbox = text.get_rect()
textbox.center = (500, 500)

while True:
    """main game loop"""

    # checks if the user has pressed q
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                exit_game(image_frames)

    # displays the background for the field
    background = pygame.image.load("field.png")
    screen.blit(background, (0, 0))

    normal_tile_colour = (164, 83, 38)
    touching_mouse_tile_colour = (204, 124, 38)

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

            # gets mouse location
            (mousex, mousey) = pygame.mouse.get_pos()

            # check if tile is touching mouse, if it is use the brighter colour
            if (tilex < mousex < tilex + 100) and (tiley < mousey < tiley + 100):
                pygame.draw.rect(screen, touching_mouse_tile_colour, tile)
            else:
                pygame.draw.rect(screen, normal_tile_colour, tile)

            # next iteration of inner loop
            x += 1
        
        # next iteration of outer loop
        y += 1

    # updates the display and a small delay so that the game mechanics dont go so fast
    pygame.display.update()

    # takes screenshot then adds data to list of video frames
    # this will use up alot of ram if the recording is long
    # I will try to fix that later on
    pygame.image.save(screen, "screenshot.png")
    image_frames.append(cv2.imread("screenshot.png"))

    time.sleep(0.05)
