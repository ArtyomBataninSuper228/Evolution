import random
from math import *
import numpy as np
import pygame as pg
import copy

organizms = []
simulation_time = 0  # время с начала симуляции
h = 1 / 100  # время между итерациями модели


class Organizm:
    def __init__(self, x=0, y=0, health=100, energy=100, speed=10, color=(0, 0, 0), generation=0,
                 radius_of_view=100, parents=[], gender="male", icon=None):
        global organizms, simulation_time
        self.x = x
        self.y = y
        self.health = health # Относительное здоровье ( от 0 до 1)
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


class Ship(Organizm):
    def __init__(self, x, y, gender):
        super().__init__(x = x, y= y, gender= gender)
        self.brave = 0

    def update(self):
        if self.health<= 0:
            organizms.remove(self)
        enemies = []
        plants = []
        partners = []
        ships = []
        for organizm in organizms:
            if sqrt((organizm.x - self.x)**2 + (organizm.y - self.y)**2) <= self.radius_of_view:
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



class Wolf(Organizm):
    def __init__(self, x, y, gender):
        super().__init__(x = x, y= y, gender= gender)
        self.brave = 0

    def analyzing(self):
        for organizm in organizms:
            pass
class Plant(Organizm):
    def __init__(self, x, y):
        super().__init__(x = x, y= y)



a = Ship(0,0, 'male')
print(type(a))
