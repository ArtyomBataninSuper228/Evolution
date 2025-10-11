import random
from math import *
import numpy as np
import pygame as pg
import copy

from pandas.conftest import rand_series_with_duplicate_datetimeindex

organizms = []
simulation_time = 0  # время с начала симуляции
h = 1 / 100  # время между итерациями модели
mutationfactor = 0.1


def radius(o1, o2):
    return((o1.x - o2.x)**2 + (o1.y - o2.y)**2)**0.5

class Organizm:
    def __init__(self, x=0, y=0, health=100, energy=100, speed=10, color=(0, 0, 0), generation=0,
                 radius_of_view=100, parents=[], gender="male", icon=None):
        global organizms, simulation_time
        self.x = x
        self.y = y
        self.health = health # Относительное здоровье ( от 0 до 1)
        self.totalhealth = 50
        self.maxhealth = 100# Максимальное значение здоровья
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


class Ship(Organizm):
    def __init__(self, x, y, gender):
        super().__init__(x = x, y= y, gender= gender)
        self.brave = 0
        self.damage = 10
        self.timeout = 1
        self.time_of_start_timeout = 0

    def update(self):
        if self.health<= 0:
            organizms.remove(self)
        if simulation_time - self.time_of_birth >= self.age_of_adult:
            self.is_adult = True
            self.totalhealth = 100
        enemies = []
        plants = []
        partners = []
        ships = []
        for organizm in organizms:
            if radius(self, organizm) <= self.radius_of_view:
                if (self.age < self.age_of_adult / 2) and(type(organizm) != Ship and type(organizm) != Plant):
                    enemies.append(organizm)
                elif (self.age < self.age_of_adult / 2) and  type(organizm) == Wolf:
                    enemies.append(organizm)
                if type(organizm) == Plant:
                    plants.append(organizm)
                if type(organizm) == Ship:
                    ships.append(organizm)
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
            if radius(self, partners[-1] < self.actionradius):
                self.energy -= 50
                partners[-1].energy -= 50
                r = self.color[0]/2 + partners[-1].color[0]/2
                g = self.color[1] / 2 + partners[-1].color[1] / 2
                b = self.color[2] / 2 + partners[-1].color[2] / 2
                r += mutationfactor* random.randint(-int(r), 255-int(r))
                g += mutationfactor * random.randint(-int(g), 255 - int(g))
                b += mutationfactor * random.randint(-int(b), 255 - int(b))
                v = self.speed/2 + partners[-1].speed/2 + random.randint(-10, 10)*mutationfactor
                dm = self.damage / 2 + partners[-1].damage / 2 + random.randint(-1, 1) * mutationfactor
                fov = self.radius_of_view/2 + partners.radius_of_view/2 + random.randint(-100, 100)*mutationfactor
                if random.randint(0, 1):
                    gender = 'male'
                else:
                    gender = 'female'
                child = Ship(self.x, self.y, gender)
                child.color = (r, g, b)
                child.speed = v
                child.radius_of_view = fov
                child.damage = dm





class Wolf(Organizm):
    def __init__(self, x, y, gender):
        super().__init__(x = x, y= y, gender= gender)
        self.brave = 0

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
                if (self.age < self.age_of_adult / 2) and type(organizm) == Ship:
                    enemies.append(organizm)
                if type(organizm) == Plant:
                    plants.append(organizm)
                if type(organizm) == Wolf:
                    wolfs.append(organizm)
                if organizm.gender != self.gender:
                    partners.append(organizm)
        if len(partners) != 0 and self.energy > 50 and self.is_adult and partners[-1].is_adult:
            def reiting(p):
                reit =0
                if p.energy <= 50:
                    return 0
                reit += p.speed
                reit += p.damage
                return reit
            partners.sort(key = reiting)
            if radius(self, partners[-1] < self.actionradius):
                self.energy -= 50
                partners[-1].energy -= 50


class Plant(Organizm):
    def __init__(self, x, y):
        super().__init__(x = x, y= y)



a = Ship(0,0, 'male')
print(type(a))
