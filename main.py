import random
import sys
import time
from math import *
from threading import Thread

import numpy as np
import pygame as pg
import copy



organizms = []
simulation_time = 0  # время с начала симуляции
h = 1 / 100000  # время между итерациями модели
mutationfactor = 0.1
is_run_sim = True
is_running = True
wolf_icon = pg.image.load('Resources/Wolf.png')
sheep_icon = pg.image.load('Resources/sheep.jpg')
plant_icon = pg.image.load('Resources/plant.png')
W = 1000
H = 800
sc = pg.display.set_mode((W, H))
scale = 1
FPS = 60
camerapos = [0, 0]


def radius(o1, o2):
    return((o1.x - o2.x)**2 + (o1.y - o2.y)**2)**0.5


class Organizm:
    def __init__(self, x=0, y=0, health=100, energy=100, speed=10, color=(0, 0, 0), generation=0,
                 radius_of_view=100, parents=[], gender="male", icon=None):
        global organizms, simulation_time
        self.x = x
        self.y = y
        self.health = health # Относительное здоровье (от 0 до 1)
        self.totalhealth = 50
        self.maxhealth = 100# Максимальное значение здоровья взрослого
        self.kreg = 0.01# коэффициент регенерации
        self.kmoove = 0.01# коэффициент затраты энергии на перемещение
        self.actionradius = 1 # радиус действия (есть или драться)
        self.energy = energy
        self.speed = speed
        self.color = color
        self.generation = generation
        self.radius_of_view = radius_of_view
        self.time_of_birth = simulation_time
        self.is_adult = False
        self.age = 0
        self.age_of_adult = 600
        self.maxage = 60*60
        self.parents = parents
        self.gender = gender
        self.icon = icon
        self.previous_move = [0, 0]
        organizms.append(self)

    def go(self, vector):
        global h
        self.x += vector[0] * self.speed * h
        self.y += vector[1] * self.speed * h
        if self.energy >= self.kmoove*h:
            self.energy -= self.kmoove*h
        else:
            self.health -= self.kmoove*h
    def eat(self, who):
        self.energy += who.energy
        self.energy += who.health/2
        organizms.remove(who)


class Sheep(Organizm):
    def __init__(self, x, y, gender):
        super().__init__(x = x, y= y, gender= gender)
        self.brave = 0
        self.damage = 10
        self.timeout = 1
        self.time_of_start_timeout = 0
        self.icon = sheep_icon

    def update(self):
        if self.health<= 0:
            organizms.remove(self)
        if simulation_time - self.time_of_birth >= self.age_of_adult:
            self.is_adult = True
            self.totalhealth = 100
        self.age = simulation_time - self.time_of_birth
        if self.age >= self.maxage:
            organizms.remove(self)


        enemies = []
        plants = []
        partners = []
        sheeps = []
        for organizm in organizms:
            if radius(self, organizm) <= self.radius_of_view:
                if (self.age < self.age_of_adult / 2) and(type(organizm) != Sheep and type(organizm) != Plant):
                    enemies.append(organizm)
                elif (self.age < self.age_of_adult / 2) and  type(organizm) == Wolf:
                    enemies.append(organizm)
                if type(organizm) == Plant:
                    plants.append(organizm)
                if type(organizm) == Sheep:
                    sheeps.append(organizm)
                    if organizm.gender != self.gender:
                        partners.append(organizm)
        if len(enemies) != 0:
            xs = 0
            ys = 0
            for enemy in enemies:
                xs += enemy.x/len(enemies)
                ys += enemy.y/len(enemies)
            deltax = self.x - xs
            deltay =  self.y - ys
            l = (deltax*2 + deltay**2)**0.5
            self.previous_move = [deltax/l, deltay/l]
            self.go(self.previous_move)
            def f(v):
                return radius(self, v)
            enemies.sort(key = f)
            if radius(self, enemies[0]) < self.actionradius and simulation_time - self.time_of_start_timeout >= self.timeout:
                enemies[0].health -= self.damage/enemies[0].maxhealth
                if self.energy > 1:
                    self.energy -= 1
                else:
                    self.health -= 1
                self.time_of_start_timeout = simulation_time
            return
        if len(partners) != 0 and self.energy > 50 and self.is_adult and partners[-1].is_adult:
            def reiting(p):
                reit =0
                if p.energy <= 50:
                    return 0
                reit += abs(self.color[0] - p.color[0])
                reit += abs(self.color[1] - p.color[1])
                reit += abs(self.color[2] - p.color[2])
                reit += p.speed
                reit += p.damage
                return reit
            partners.sort(key = reiting)
            if reiting(partners[-1]) > 0:
                deltax = partners[-1].x - self.x
                deltay = partners[-1].y - self.y
                l = (deltax * 2 + deltay ** 2) ** 0.5
                self.previous_move = [deltax / l, deltay / l]
                self.go(self.previous_move)
            if radius(self, partners[-1] < self.actionradius):
                self.energy -= 50
                partners[-1].energy -= 50
                r = self.color[0]/2 + partners[-1].color[0]/2
                g = self.color[1] / 2 + partners[-1].color[1] / 2
                b = self.color[2] / 2 + partners[-1].color[2] / 2
                r += mutationfactor * random.randint(-int(r), 255 - int(r))
                g += mutationfactor * random.randint(-int(g), 255 - int(g))
                b += mutationfactor * random.randint(-int(b), 255 - int(b))
                v = self.speed/2 + partners[-1].speed/2 + random.randint(-10, 10)*mutationfactor
                dm = self.damage / 2 + partners[-1].damage / 2 + random.randint(-1, 1) * mutationfactor
                fov = self.radius_of_view/2 + partners[-1].radius_of_view/2 + random.randint(-100, 100)*mutationfactor


                gender = "male" if random.random() < 0.5 else "female"
                child = Sheep(self.x, self.y, gender)
                child.color = (r, g, b)
                child.speed = v
                child.radius_of_view = fov
                child.damage = dm
                child.parents = [self, partners[-1]]

        if len(plants)!= 0:
            def rt(p):
                return radius(self, p)
            plants.sort(key = rt)
            deltax = plants[-1].x - self.x
            deltay = plants[-1].y - self.y
            l = (deltax * 2 + deltay ** 2) ** 0.5
            self.previous_move = [deltax / l, deltay / l]
            self.go(self.previous_move)







class Wolf(Organizm):
    def __init__(self, x, y, gender):
        super().__init__(x = x, y= y, gender= gender)
        self.damage = 20
        self.icon = wolf_icon
        self.timeout = 1
        self.time_of_start_timeout = 0


    def update(self):
        if self.health<= 0:
            organizms.remove(self)
        if simulation_time - self.time_of_birth >= self.age_of_adult:
            self.is_adult = True
        enemies = []
        plants = []
        partners = []
        wolfs = []
        for organizm in organizms:
            if radius(self, organizm) <= self.radius_of_view:
                if type(organizm) == Sheep:
                    enemies.append(organizm)
                if type(organizm) == Plant:
                    plants.append(organizm)
                if type(organizm) == Wolf:
                    wolfs.append(organizm)
                if organizm.gender != self.gender and organizm.is_adult and self.is_adult:
                    partners.append(organizm)
        if len(partners) != 0 and self.energy > 50:
            def reiting(p):
                reit =0
                if p.energy <= 50:
                    return 0
                reit += abs(self.color[0] - p.color[0])
                reit += abs(self.color[1] - p.color[1])
                reit += abs(self.color[2] - p.color[2])
                reit += p.speed
                reit += p.damage
                return reit
            partners.sort(key = reiting)
            if radius(self, partners[-1] < self.actionradius):
                self.energy -= 50
                partners[-1].energy -= 50


                r = self.color[0]/2 + partners[-1].color[0]/2
                g = self.color[1] / 2 + partners[-1].color[1] / 2
                b = self.color[2] / 2 + partners[-1].color[2] / 2
                r += mutationfactor * random.randint(-int(r), 255 - int(r))
                g += mutationfactor * random.randint(-int(g), 255 - int(g))
                b += mutationfactor * random.randint(-int(b), 255 - int(b))
                v = self.speed/2 + partners[-1].speed/2 + random.randint(-10, 10)*mutationfactor
                dm = self.damage / 2 + partners[-1].damage / 2 + random.randint(-1, 1) * mutationfactor
                fov = self.radius_of_view/2 + partners[-1].radius_of_view/2 + random.randint(-100, 100)*mutationfactor


                gender = "male" if random.random() < 0.5 else "female"
                child = Sheep(self.x, self.y, gender)
                child.color = (r, g, b)
                child.speed = v
                child.radius_of_view = fov
                child.damage = dm
                child.parents = [self, partners[-1]]


        if len(enemies) > 0 and self.energy < 70:

            def distancia(x):
                return radius(self, x)
            enemies.sort(key=distancia)
            blizayshiy = enemies[0]
            deltax = blizayshiy.x - self.x
            deltay = blizayshiy.y - self.y
            l = (deltax * 2 + deltay ** 2) ** 0.5
            self.previous_move=[deltax / l, deltay / l]
            self.go(self.previous_move)


            if l < self.actionradius and simulation_time - self.time_of_start_timeout >= self.timeout:
                self.energy -= 1
                if blizayshiy.health*blizayshiy.maxhealth < self.damage:
                    self.eat(blizayshiy)
                else:
                    blizayshiy.health -= self.damage/blizayshiy.maxhealth
                self.time_of_start_timeout = simulation_time





class Plant(Organizm):
    def __init__(self, x, y):
        super().__init__(x = x, y= y)
        self.energy = 100
        self.health = 25
        self.icon = plant_icon
    def update(self):
        pass




#a = Sheep(0,0, 'male')
#b = Sheep(0,0, 'female')
Plant(0, 0)
s = Sheep(100, 100, "male")
s.radius_of_view = 1000

#Main loop
def main_loop():
    while is_running:
        while is_run_sim:
            for organizm in organizms:
                organizm.update()
        time.sleep(1 / 10)
t = Thread(target=main_loop)
t.start()




#Render loop
while is_running:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            sys.exit()
    keys = pg.key.get_pressed()
    if keys[pg.K_w]:
        camerapos[1] += 10/FPS/scale
    if keys[pg.K_s]:
        camerapos[1] -= 10/FPS/scale
    if keys[pg.K_a]:
        camerapos[0] -= 10 / FPS / scale
    if keys[pg.K_d]:
        camerapos[0] += 10/FPS/scale
    if keys[pg.K_i]:
        scale /= 1.1
    if keys[pg.K_k]:
        scale *= 1.1

    sc.fill((0, 0, 0))
    for organizm in organizms:
        x = (organizm.x + camerapos[0])*scale + 500
        y = (organizm.y - camerapos[1])*scale + 400
        sc.blit(organizm.icon, (x,y))
    pg.display.update()

