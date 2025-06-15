#pygame script for basic interaction thingy (very buggy)

class vector2:

    def __init__(self, x, y):

        self.x = x
        self.y = y

    def __add__(self, vector):
        new_vector = vector2(self.x + vector.x, self.y + vector.y)
        return new_vector

    def __sub__(self, vector):
        new_vector = vector2(self.x - vector.x, self.y - vector.y)
        return new_vector

    def __mul__(self, scalar):
        new_vector = vector2(self.x * scalar, self.y * scalar)
        return new_vector

    def __truediv__(self, scalar):
        new_vector = vector2(self.x / scalar, self.y / scalar)
        return new_vector

    def dot(self, vector):
        dot = self.x * vector.x + self.y * vector.y
        return dot
    
class camera:

    def __init__(self, x, y):

        self.position = vector2(x,y)
        self.zoom = 1
        self.offset = vector2(0,0)

import random

class body:

    def __init__(self, x, y, radius = random.randint(20,50), mass = 1, xSpeed = 0, ySpeed = 0):

        self.mass = mass
        self.radius = radius
        self.position = vector2(x, y)
        self.speed = vector2(xSpeed, ySpeed)

import pygame as pg
import math

#initialize variables
bodies = [body(0, 0, 50, 100)]
G = 0.0000000000667408

#initialize pg
pg.init()
clock = pg.time.Clock()
dt = 0
screen_height = 900
screen_width = 900

#gets screen resolution
#info_object = pg.display.Info()

#sets up camera
camera = camera(0,0)
camera_offset = [screen_width/2, screen_height/2]
camera.offset = vector2(0, 0)
move_camera = False

#sets up the screen to display the game
#screen = pg.display.set_mode((info_object.current_w, info_object.current_h), pg.FULLSCREEN)
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Space Simulation")

done = False

while not done:
    for event in pg.event.get():
        #end the game if the user closes it
        if event.type == pg.QUIT:
            done = True

        #check to see if the mouse has been pressed
        if event.type == pg.MOUSEBUTTONDOWN:
            #lmb
            if event.button == 1:
                pos = pg.mouse.get_pos()
                bodies.append(body(int((pos[0]-camera_offset[0])/camera.zoom + camera.position.x), int((pos[1]-camera_offset[1])/camera.zoom + camera.position.y)))

            #mmb
            if event.button == 2:
                move_camera = True
                start_pos = pg.mouse.get_pos()

            if event.button == 4:
                camera.zoom *= 1.1

            if event.button == 5:
                camera.zoom *= 0.9

        if event.type == pg.MOUSEBUTTONUP:
            #rmb
            if event.button == 2:
                move_camera = False

        if move_camera == True:

            end_pos = pg.mouse.get_pos()

            moved = [end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]]

            camera.position.x -= moved[0]/camera.zoom
            camera.position.y -= moved[1]/camera.zoom

            start_pos = pg.mouse.get_pos()

    for subject in bodies:

        attraction = vector2(0,0)

        for attractor in bodies:

            if attractor != subject:
                distance = math.sqrt((attractor.position.x - subject.position.x)**2 + (attractor.position.y - subject.position.y)**2)
                if distance != 0:
                    attraction += (attractor.position - subject.position) * (attractor.mass/((distance)**3))

        subject.speed = subject.speed + ((attraction * dt)/subject.mass)

        subject.position = subject.position + (subject.speed * dt)


    screen.fill((0,0,0))

    for active_body in bodies:
        pg.draw.circle(screen, (0,0,255),
         (int(active_body.position.x*camera.zoom - camera.position.x*camera.zoom + camera_offset[0]),
          int(active_body.position.y*camera.zoom - camera.position.y*camera.zoom + camera_offset[1])),
           int(active_body.radius*camera.zoom))

    pg.display.flip()

    dt = clock.tick(60)