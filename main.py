from math import *
import numpy as np
import pygame as pg

organizms = []
simulation_time = 0
h = 0


class Organizm:
    def __init__(self, x, y, health = 100, energy = 100, speed = 10, color = (0,0,0), generation = 0, type = "plant", radius_of_view = 100, parents = [], gender = "male"):
        global organizms, simulation_time
        self.x = x
        self.y = y
        self.health = health
        self.energy = energy
        self.speed = speed
        self.color = color
        self.generation = generation
        self.type = type
        self.radius_of_view = radius_of_view
        self.time_of_birth = simulation_time
        self.age = 0
        self.parents = parents
        self.gender = gender
        organizms.append(self)
    def go(self, vector):
        self.x += vector[0]*self.speed
        self.y  += vector[1] * self.speed
class Ship (Organizm):
    def __init__(self, x, y, class_gender):
        super.__init__(x, y, gender = class_gender)
        self.brave = 0


