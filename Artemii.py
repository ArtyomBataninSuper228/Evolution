import pygame
import sys
from random import randint as rnd
from random import shuffle, random
import math

pygame.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Creature Example")

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

cellsize = 30
cellsx = round(1920 / cellsize)
cellsy = round(1080 / cellsize)
colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255),
          (125, 0, 0), (0, 125, 0), (0, 0, 125), (125, 125, 0), (0, 125, 125), (125, 0, 125),
          (255, 125, 0), (125, 255, 0), (0, 255, 125), (0, 125, 255), (255, 0, 125), (125, 0, 255), (125, 125, 125), (0, 0, 0)]
shuffle(colors)
map = {}

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, parent=None):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        # Случайная инициализация весов
        self.weights_input_hidden = [[random() * 2 - 1 for _ in range(hidden_size)] for _ in range(input_size)]
        self.weights_hidden_output = [[random() * 2 - 1 for _ in range(output_size)] for _ in range(hidden_size)]
        self.output_threshold = 0.2  # Порог активации выходного нейрона
        if parent:
            # Наследование весов от родителя
            self.weights_input_hidden = [row[:] for row in parent.brain.weights_input_hidden]
            self.weights_hidden_output = [row[:] for row in parent.brain.weights_hidden_output]
            self.output_threshold = parent.brain.output_threshold

    def mutate(self):
        # Мутация весов
        for i in range(self.input_size):
            for j in range(self.hidden_size):
                self.weights_input_hidden[i][j] += (random() - 0.5) * BRAIN_MUTATION_RATE
                self.weights_input_hidden[i][j] = max(-1, min(1, self.weights_input_hidden[i][j]))

        for i in range(self.hidden_size):
            for j in range(self.output_size):
                self.weights_hidden_output[i][j] += (random() - 0.5) * BRAIN_MUTATION_RATE
                self.weights_hidden_output[i][j] = max(-1, min(1, self.weights_hidden_output[i][j]))

        # Мутация порога
        self.output_threshold += (random() - 0.5) * 0.3 * BRAIN_MUTATION_RATE
        self.output_threshold = max(0, min(0.9, self.output_threshold))

    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))

    def forward(self, inputs):
        # Прямое распространение через скрытый слой
        hidden = [0] * self.hidden_size
        for j in range(self.hidden_size):
            for i in range(self.input_size):
                hidden[j] += inputs[i] * self.weights_input_hidden[i][j]
            hidden[j] = self.sigmoid(hidden[j])

        # Прямое распространение через выходной слой
        outputs = [0] * self.output_size
        for j in range(self.output_size):
            for i in range(self.hidden_size):
                outputs[j] += hidden[i] * self.weights_hidden_output[i][j]
            outputs[j] = self.sigmoid(outputs[j])

        return outputs


class Widget:
    def __init__(self, text, pos, lifetime="endless", size=36):
        self.text = text
        self.lifetime = lifetime
        self.pos = pos
        self.font = f1 = pygame.font.Font(None, size)

    def tick(self):
        if self.lifetime != "endless":
            self.lifetime -= 1
            if self.lifetime <= 0:
                return "death"

    def draw(self):
        text1 = self.font.render(self.text, 1, (0, 0, 0))
        screen.blit(text1, self.pos)


class Creature:
    def __init__(self, x, y, vector, genome=0, color=0, parent=None):
        self.x = x
        self.y = y
        self.food = 0
        self.age = 0
        self.vector = vector
        self.i = 0
        self.color = color
        self.mustmultiple = False
        self.health = 3
        self.attacking = False
        self.parent = parent
        self.protected = False
        self.damaged_last_turn = 0  # 1 если получил урон в предыдущем ходу, иначе 0

        # Инициализация нейросети
        self.brain = NeuralNetwork(6, 6, 6, parent)

        self.generateGenome(genome)

        map[(x, y)] = self

    def draw(self, surface):
        color = colors[self.color]
        updated_color = []
        for col in color:
            col *= (5 - self.age) / 5
            col = max(col, 0)
            col = min(col, 255)
            updated_color.append(col)
        color2 = (255, 255, 0)
        if self.attacking == True: color2 = (255, 0, 0)
        if self.protected == True: color2 = (0, 0, 255)
        pygame.draw.rect(surface, color2, (self.x * cellsize + 1 + self.vector[0] * 3, self.y * cellsize + 1 + self.vector[1] * 3, cellsize - 2, cellsize - 2))
        pygame.draw.rect(surface, updated_color, (self.x * cellsize + 1, self.y * cellsize + 1, cellsize - 2, cellsize - 2))

    def tick(self):
        self.age += 0.01
        self.food += 0.72
        self.food -= self.age

        if self.food < 0:
            map[(self.x, self.y)] = 0
            return "death"
        if self.health <= 0:
            map[(self.x, self.y)] = 0
            return "death"

        # Получение входных данных для нейросети
        inputs = self.get_inputs()

        # Получение выходных данных от нейросети
        outputs = self.brain.forward(inputs)

        # Проверка, есть ли выходной нейрон с достаточно высоким значением
        max_output = max(outputs)
        if max_output > self.brain.output_threshold:
            # Использование решения нейросети
            action_index = outputs.index(max_output)
            self.execute_neural_action(action_index)
        else:
            # Использование генома
            if self.i >= len(self.genome):
                self.i = 0
            self.genome[self.i]()
            self.i += 1

        # Сброс флага урона для следующего хода
        self.damaged_last_turn = 0

        if self.food >= 15 or self.mustmultiple:
            self.mustmultiple = False
            return "multiple"

    def get_inputs(self):
        # 1) Количество еды (нормализованное)
        food_input = min(self.food / 15.0, 1.0)

        # 2) Возраст клетки (нормализованный)
        age_input = min(self.age / 5.0, 1.0)

        # 3) Кто стоит перед клеткой
        new_x = self.x + self.vector[0]
        new_y = self.y + self.vector[1]
        creature_ahead = map.get((new_x, new_y), 0)
        bro = 0
        not_bro = 0
        protected = 0
        if type(creature_ahead) == Creature:
            if creature_ahead.getColor() == self.color:
                bro = 1  # Свой вид
            else:
                not_bro = -1  # Чужой вид
            protected = creature_ahead.protected
        # 4) Получила ли клетка урон в предыдущем ходу
        damage_input = self.damaged_last_turn

        return [food_input, age_input, bro, not_bro, protected, damage_input]

    def execute_neural_action(self, action_index):
        # Выполнение действия на основе выхода нейросети
        actions = [
            self.rotateRight,
            self.rotateLeft,
            self.move,
            self.wait,
            self.attack,
            self.defend
        ]

        if action_index < len(actions):
            actions[action_index]()

            # Установка флагов атаки и защиты
            if action_index == 4:  # Атака
                self.attacking = True
            else:
                self.attacking = False

            if action_index == 5:  # Защита
                self.protected = True
            else:
                self.protected = False

    def getpos(self):
        return self.x, self.y

    def getvector(self):
        return self.vector

    def setfood(self, arg):
        self.food = arg

    def getfood(self):
        return self.food

    def rotateRight(self):
        self.vector = (self.vector[1], -self.vector[0])

    def rotateLeft(self):
        self.vector = (-self.vector[1], self.vector[0])

    def move(self):
        new_x = self.x + self.vector[0]
        new_y = self.y + self.vector[1]
        c = map.get((new_x, new_y), 0)
        if c == 0:
            map[(self.x, self.y)] = 0
            self.x = new_x
            self.y = new_y
            map[(self.x, self.y)] = self

    def wait(self):
        pass

    def multiple(self):
        if self.food > 10:
            self.mustmultiple = True

    def getGenome(self):
        return self.genome

    def getConvertedGenome(self):
        return self.convertedGenome

    def getColor(self):
        return self.color

    def damage(self):
        if self.protected == False:
            self.health = -1
            self.damaged_last_turn = 1  # Устанавливаем флаг урона
        else:
            #бонус за успешное блокирование атаки
            self.food += 5

    def attack(self):
        new_x = self.x + self.vector[0]
        new_y = self.y + self.vector[1]
        c = map.get((new_x, new_y), 0)
        if c != 0:
            c.damage()
            self.food += 10

    def defend(self):
        self.protected = True

    def generateGenome(self, gen):
        if gen == 0:
            gen = ""
            for i in range(rnd(2, 3)):
                gen += str(rnd(1, 6))
            print(f"Стартовый геном: {gen}")
        gen = str(gen)
        self.genome = []
        if rnd(1, mutationsRate) == mutations:
            #Код для мутации
            self.color = rnd(0, len(colors) - 1)
            l = len(gen)
            if rnd(1, 2) == 1 and l > 1:
                index_to_remove = rnd(0, len(gen) - 1)
                gen = gen[:index_to_remove] + gen[index_to_remove + 1:]
            else:
                index_to_remove = rnd(0, len(gen) - 1)
                gen = gen[:index_to_remove + 1] + str(rnd(1, 6)) + gen[index_to_remove + 1:]
            self.brain.mutate()
        self.convertedGenome = gen
        for i in gen: self.genome.append([self.rotateRight, self.rotateLeft, self.move, self.wait, self.attack, self.defend][int(i)-1])


def multiple(creature):
    x, y = creature.getpos()
    new_x = x + creature.getvector()[0]
    new_y = y + creature.getvector()[1]
    if new_x > 0 and new_y > 0:
        if new_x < cellsx - 1 and new_y < cellsy - 1:
            c = map.get((new_x, new_y), 0)
            if c == 0:
                creature.setfood(creature.getfood() - 10)
                new_creature = Creature(new_x, new_y, creature.getvector(), genome=creature.getConvertedGenome(), color=creature.getColor(), parent=creature)
                creatures.append(new_creature)


def main():
    global widgets
    clock = pygame.time.Clock()
    pause = False
    fps = 5
    while True:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    pause = not pause
                elif event.key == pygame.K_1:
                    fps += 5
                elif event.key == pygame.K_2:
                    fps -= 5
                elif event.key == pygame.K_3:
                    for i in creatures:
                        i.setfood(-999)
                    creatures.append(Creature(round(cellsx / 2), round(cellsy / 2), (1, 0)))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                p = pygame.mouse.get_pos()
                x = p[0]
                x = round(round(x + 0.5) / cellsize)
                y = p[1]
                y = round(round(y + 0.5) / cellsize)
                try:
                    g = map.get((x, y), 0)
                    gen = g.getConvertedGenome()
                    text = gen
                except:
                    text = "Существа не обнаружены"
                    continue
                widgets = []
                sdvig = 0
                for i in range(len(str(text))):
                    sdvig += 30
                    widgets.append(Widget(text=f'{i+1}.{["Направо", "Налево", "Вперёд", "Ждать", "Атака", "Защита"][int(str(text)[i])-1]}', lifetime=60,
                                          pos=(1920 * 0.8, 1080 * 0.07 + sdvig)))
                if type(g) == Creature:
                    sdvig_x = 150
                    for mainlist in [g.brain.weights_input_hidden, g.brain.weights_hidden_output]:
                        sdvig = 0
                        for sublist in mainlist:
                            for i in sublist:
                                sdvig += 15
                                widgets.append(Widget(text=f"{round(i, 2)}", pos=(1920 * 0.8 + sdvig_x, 1080 * 0.07 + sdvig), lifetime=60))
                        sdvig_x += 100
        for creature in creatures:
            if not pause:
                result = creature.tick()
            creature.draw(screen)
            if result == "death":
                creatures.remove(creature)
                del creature
            if result == "multiple":
                multiple(creature)
        for widget in widgets:
            if widget.tick() == "death":
                widgets.remove(widget)
                del widget
            else:
                widget.draw()

        pygame.display.flip()
        clock.tick(fps)

BRAIN_MUTATION_RATE = 2
pause = False
mutations = 1
mutationsRate = 50
widgets = []
creatures = [Creature(round(cellsx / 2), round(cellsy / 2), (1, 0))]
main()