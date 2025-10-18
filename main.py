import random
import sys
import time
from math import *
from threading import Thread
from matplotlib import pyplot as plt
import numpy as np
import pygame as pg
import copy



organizms = []
simulation_time = 0  # время с начала симуляции
h = 1 / 20  # время между итерациями модели
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
    def __init__(self, x=0, y=0, health=1, energy=20, speed=10, color=(0, 0, 0), generation=0,
                 radius_of_view=200, parents=[], gender="male", icon=None):
        global organizms, simulation_time
        self.x = x
        self.y = y
        self.health = health # Относительное здоровье (от 0 до 1)
        self.totalhealth = 50
        self.maxhealth = 100# Максимальное значение здоровья взрослого
        self.kreg = 0.1# коэффициент регенерации
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
        self.age_of_adult = 60
        self.maxage = 60*4
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
        self.damage = 2
        self.timeout = 1
        self.time_of_start_timeout = 0
        self.icon = sheep_icon
        self.target = None
        self.a = 1000
        self.b = 1000
        self.c = 1000
        self.d = 0.1
        self.time_of_birth = simulation_time
        self.is_adult = False


    def update(self):
        if self.health<= 0:

            organizms.remove(self)
        if simulation_time - self.time_of_birth >= self.age_of_adult:
            if self.is_adult == False:
                self.energy  = 10
            self.is_adult = True
            self.totalhealth = 100

        self.age = simulation_time - self.time_of_birth
        if simulation_time - self.time_of_birth >= self.maxage:

            organizms.remove(self)
        if self.health < 1:
            self.health += self.kreg/self.totalhealth
            self.energy -= self.kreg


        enemies = []
        plants = []
        partners = []
        sheeps = []
        for organizm in organizms:
            if radius(self, organizm) <= self.radius_of_view:
                if (self.age < self.age_of_adult / 2) and(type(organizm) != Sheep and type(organizm) != Plant):
                    enemies.append(organizm)
                if type(organizm) == Wolf:
                    enemies.append(organizm)
                if type(organizm) == Plant:
                    plants.append(organizm)
                if type(organizm) == Sheep:
                    sheeps.append(organizm)
                    if organizm.gender != self.gender and organizm.is_adult :
                        partners.append(organizm)
        A = 0
        B = 0
        C = 0
        D = self.d
        for enemy in enemies:
            A += self.a/radius(self, enemy)

        if self.energy > 50 and len(partners) > 0 and self.is_adult and self.energy > 50:
            def reiting(partner):
                rt = 0
                rt += abs(self.color[0] - partner.color[0]) + abs(self.color[1] - partner.color[1])+ abs(self.color[2] - partner.color[2])
                rt += partner.damage
                rt += partner.speed
                return rt
            for partner in partners:
                try:
                    B += self.b*reiting(partner)/radius(self, partner)
                except ZeroDivisionError:
                    B += self.b*reiting(partner)/1

        for plant in plants:
            C +=   1/(1+self.energy)*self.c/radius(self, plant)
        m = [["A", A], ["B", B], ["C", C]]
        def f(el):
            return(el[1])
        m.sort(key=f)
        if m[-1][1] != 0:
           KEY  = m[-1][0]
        else:
            KEY = "D"
        if KEY == "A":
            x = 0
            y = 0
            for enemy in enemies:
                x += enemy.x
                y +=  enemy.y
            x /= len(enemies)
            y /= len(enemies)
            dx = x - self.x
            dy = y - self.y
            l = abs(dx**2 + dy**2)**0.5
            self.previous_move = [-dx/l, -dy/l]
            self.go(self.previous_move)
            def f(x):
                return radius(self, x)
            enemies.sort(key=f)
            if radius(self, enemies[0]) < self.actionradius and simulation_time - self.time_of_start_timeout >= self.timeout:
                enemies[-1].health -= self.damage/enemies[-1].totalhealth
                self.time_of_start_timeout = simulation_time

        if KEY == "B":
            def reiting(partner):
                rt = 0
                rt += abs(self.color[0] - partner.color[0]) + abs(self.color[1] - partner.color[1]) + abs(
                    self.color[2] - partner.color[2])
                rt += partner.damage
                rt += partner.speed
                return rt
            partners.sort(key=reiting)
            partner = partners[-1]

            dx = partner.x - self.x
            dy = partner.y - self.y
            l = (dx**2 + dy**2)**0.5
            if l != 0:
                self.previous_move = [dx/l, dy/l]
                self.go(self.previous_move)

            if radius(self, partner) <= self.actionradius and simulation_time- self.time_of_start_timeout > self.timeout:
                self.time_of_start_timeout = simulation_time
                partner.time_of_start_timeout = simulation_time
                self.energy -= 50
                partner.energy -= 50
                r = self.color[0]/2 + partner.color[0]/2
                g = self.color[1] / 2 + partner.color[1] / 2
                b = self.color[2] / 2 + partner.color[2] / 2
                r += mutationfactor*random.randint(int(-r), 255 - int(r))
                g += mutationfactor*random.randint(int(-g), 255 - int(g))
                b += mutationfactor*random.randint(int(-b), 255 - int(b))

                speed = self.speed/2 + partner.speed/2 + mutationfactor*random.randint(-10, 10)
                damage = self.damage/2 + partner.damage/2 + mutationfactor*random.randint(-1, 1)
                a = self.a/2 + partner.a/2 + mutationfactor*random.randint(-1, 1)
                b = self.b/2 + partner.b/2 + mutationfactor*random.randint(-1, 1)
                c = self.c/2 + partner.c/2 + mutationfactor*random.randint(-1, 1)
                gender = "male" if random.random() < 0.5 else "female"
                child = Sheep(self.x + random.randint(-10, 10), self.y + random.randint(-10, 10), gender)

                child.r = r
                child.g = g
                child.b = b
                child.a = a
                child.b = b
                child.c = c
                child.speed = speed
                child.damage = damage
                child.parents = [self, partner]


        if KEY == "C" and len(plants) > 0:
            def f(plant):
                return radius(self, plant)


            plants.sort(key=f)
            plant = plants[0]
            dx = plant.x - self.x
            dy = plant.y - self.y
            l = (dx**2 + dy**2)**0.5
            self.previous_move = [dx/l, dy/l]
            self.go(self.previous_move)
            if radius(self, plant) <= self.actionradius:
                self.eat(plant)










class Wolf(Organizm):
    def __init__(self, x, y, gender):
        super().__init__(x = x, y= y, gender= gender)
        self.damage = 10
        self.icon = wolf_icon
        self.timeout = 1
        self.time_of_start_timeout = 0
        self.speed = 20
        self.radius_of_view = 400
        self.time_of_view = simulation_time


    def update(self):
        if self.health<= 0:
            organizms.remove(self)
        if simulation_time - self.time_of_birth >= self.age_of_adult:
            self.is_adult = True
            self.damage = 30
        if simulation_time-self.time_of_birth > self.maxage:
            organizms.remove(self)
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

        def reiting(p):
            reit = 0

            if p.energy <= 50:
                return 0
            reit += abs(self.color[0] - p.color[0])
            reit += abs(self.color[1] - p.color[1])
            reit += abs(self.color[2] - p.color[2])
            reit += p.speed
            reit += p.damage
            return reit

        partners.sort(key=reiting)
        if len(partners) != 0 and self.energy > 50 and reiting(partners[-1])>0:


            partner = partners[-1]
            dx = partner.x - self.x
            dy = partner.y - self.y
            l = (dx**2 + dy**2)**0.5
            self.previous_move = [dx/l, dy/l]
            self.go(self.previous_move)


            if radius(self, partners[-1] )< self.actionradius:
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
                child = Wolf(self.x + random.randint(-10, 10), self.y+ random.randint(-10, 10), gender)
                child.color = (r, g, b)
                child.speed = v
                child.radius_of_view = fov
                child.damage = dm
                child.parents = [self, partners[-1]]
            return


        if len(enemies) > 0:
            def distancia(x):
                return radius(self, x)
            enemies.sort(key=distancia)
            blizayshiy = enemies[0]
            deltax = blizayshiy.x - self.x
            deltay = blizayshiy.y - self.y
            l = (deltax ** 2 + deltay ** 2) ** 0.5
            self.previous_move=[deltax / l, deltay / l]
            self.go(self.previous_move)
            if l < self.actionradius and simulation_time - self.time_of_start_timeout >= self.timeout:
                self.energy -= 1
                if blizayshiy.health*blizayshiy.maxhealth < self.damage:
                    self.eat(blizayshiy)
                else:
                    blizayshiy.health -= self.damage/blizayshiy.maxhealth
                    self.time_of_start_timeout = simulation_time
            return

        x = 0
        y = 0
        for i in wolfs:
            x += i.x
            y += i.y
        x /= len(wolfs)
        y /= len(wolfs)
        deltax = x - self.x
        deltay = y - self.y
        l = (deltax ** 2 + deltay ** 2) ** 0.5
        self.previous_move = [deltax / l, deltay / l]
        self.go(self.previous_move)








class Plant(Organizm):
    def __init__(self, x, y):
        super().__init__(x = x, y= y)
        self.energy = 100
        self.health = 4
        self.icon = plant_icon
    def update(self):
        pass




#a = Sheep(0,0, 'male')
#b = Sheep(0,0, 'female')
for i in range(120):
    Plant(random.randint(-W, W), random.randint(-H, H))
    s = Sheep(random.randint(-W, W), random.randint(-H, H), "male" if random.randint(0, 1) == 1 else "female")
    s.energy = 100


for i in range(20):
    w = Wolf(random.randint(-W, W), random.randint(-H, W), gender="male" if random.randint(0, 1) == 1 else "female")

sp = 0
n = 0
for i in organizms:
    if type(i) == Sheep or type(i) == Wolf:
        sp += i.speed
        n += 1
print(sp/n)

#Main loop
def main_loop():
    global simulation_time
    while is_running:
        while is_run_sim:
            for organizm in organizms:
                if type(organizm) != Plant:
                    organizm.update()
            simulation_time += h
            if random.randint(1, 10) == 1:
                Plant(random.randint(-W, W), random.randint(-H, H))

            if simulation_time % 10 < h:
                sp = 0
                n = 0
                for i in organizms:
                    if type(i) == Sheep or type(i) == Wolf:
                        sp += i.speed
                        n += 1
                mt.append(simulation_time)
                mn.append(n)
                mv.append(sp / n)
        time.sleep(1 / 10)



mt= []
mn = []
mv = []
t = Thread(target=main_loop)
t.start()


#Render loop
while is_running:
    t1 = time.time()


    keys = pg.key.get_pressed()
    if keys[pg.K_w]:
        camerapos[1] -= 300/FPS/scale
    if keys[pg.K_s]:
        camerapos[1] += 300/FPS/scale
    if keys[pg.K_a]:
        camerapos[0] += 300 / FPS / scale
    if keys[pg.K_d]:
        camerapos[0] -= 300/FPS/scale
    if keys[pg.K_i]:
        scale *= 1.03
    if keys[pg.K_k]:
        scale /= 1.03

    sc.fill((0, 0, 0))
    for organizm in organizms:
        x = (organizm.x + camerapos[0])*scale + 500
        y = (organizm.y - camerapos[1])*scale + 400
        sc.blit(organizm.icon, (x,y))
    pg.display.update()
    t2 = time.time()
    if t2  -t1 < 1/FPS:
        time.sleep(1/FPS -(t2-t1))


    for e in pg.event.get():
        if e.type == pg.QUIT:
            is_running = False
            is_run_sim = False#
            pg.quit()

plt.plot(mt, mn)
plt.show()
plt.plot(mt, mv)
plt.show()
