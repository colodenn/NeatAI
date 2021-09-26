import pygame
import sys
import random
import os
import neat
import math
successes, failures = pygame.init()
print("Initializing pygame: {0} successes and {1} failures.".format(
    successes, failures))

SCREEN_HEIGHT = 900
SCREEN_WIDTH = 1600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
FPS = 60
FONT = pygame.font.Font('freesansbold.ttf', 20)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (91, 80, 96)


SMALL_CACTUS = [pygame.image.load(
    os.path.join("Assets/Obstacles", "tile000.png"))]
LARGE_CACTUS = [pygame.image.load(
    os.path.join("Assets/Obstacles", "tile000.png"))]


class Obstacle:
    def __init__(self, image, number_of_cacti):
        self.image = image
        self.type = number_of_cacti
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
        self.color = (random.randint(0, 255), random.randint(
            0, 255), random.randint(0, 255))

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)
        pygame.draw.rect(SCREEN, self.color, (self.rect.x,
                         self.rect.y, self.rect.width, self.rect.height), 2)


class SmallCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 450


class LargeCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 450


RUNNING = [pygame.image.load(os.path.join("Assets/BotWheel/Walk", "tile000.png")),
           pygame.image.load(os.path.join(
               "Assets/BotWheel/Walk", "tile001.png")),
           pygame.image.load(os.path.join(
               "Assets/BotWheel/Walk", "tile002.png")),
           pygame.image.load(os.path.join(
               "Assets/BotWheel/Walk", "tile003.png")),
           pygame.image.load(os.path.join(
               "Assets/BotWheel/Walk", "tile004.png")),
           pygame.image.load(os.path.join(
               "Assets/BotWheel/Walk", "tile005.png")),
           pygame.image.load(os.path.join(
               "Assets/BotWheel/Walk", "tile006.png")),
           pygame.image.load(os.path.join("Assets/BotWheel/Walk", "tile007.png"))]


JUMPING = [pygame.image.load(os.path.join(
    "Assets/BotWheel/Walk", "tile001.png"))]

SCALE = 2


class Player(pygame.sprite.Sprite):
    X_POS = 80
    Y_POS = 400
    JUMP_VEL = 8

    def __init__(self, img=RUNNING[0]):
        self.image = img

        self.dino_run = True
        self.dino_jump = False
        self.jump_vel = self.JUMP_VEL

        self.rect = pygame.Rect(self.X_POS, self.Y_POS,
                                img.get_width()/3, img.get_height())
        self.color = (random.randint(0, 255), random.randint(
            0, 255), random.randint(0, 255))
        self.step_index = 0

    def update(self):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

    def jump(self):
        self.image = JUMPING[0]
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel <= -self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL

    def run(self):
        self.image = RUNNING[self.step_index // 3 % 7]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(SCREEN, self.color, (self.rect.x,
                         self.rect.y, self.rect.width, self.rect.height), 2)
        for obstacle in obstacles:
            pygame.draw.line(SCREEN, self.color, (self.rect.x +
                             140, self.rect.y + 50), obstacle.rect.center, 2)
        # for obstacle in obstacles:
        #     pygame.draw.line(SCREEN, self.color, (self.rect.x +
        #                      54, self.rect.y + 12), obstacle.rect.center, 2)


def statistics():
    global dinosaurs, game_speed, ge
    text_1 = FONT.render(
        f'Dinosaurs Alive:  {str(len(players))}', True, (0, 0, 0))
    text_2 = FONT.render(f'Generation:  {pop.generation+1}', True, (0, 0, 0))
    text_3 = FONT.render(f'Game Speed:  {str(game_speed)}', True, (0, 0, 0))

    SCREEN.blit(text_1, (50, 750))
    SCREEN.blit(text_2, (50, 780))
    SCREEN.blit(text_3, (50, 810))


def remove(index):
    players.pop(index)
    ge.pop(index)
    nets.pop(index)


def distance(pos_a, pos_b):
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    return math.sqrt(dx**2+dy**2)


def eval_genomes(genomes, config):
    global game_speed, x_pos_bg, y_pos_bg, points, players, obstacles, ge, nets
    clock = pygame.time.Clock()
    points = 0

    obstacles = []

    players = []

    ge = []
    nets = []

    for genome_id, genome in genomes:
        players.append(Player())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    x_pos_bg = 0
    y_pos_bg = 0
    game_speed = 40

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        text = FONT.render(f'Points: {str(points)}', True, (0, 0, 0))
        SCREEN.blit(text, (700, 100))
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill(PURPLE)

        for p in players:
            p.update()
            p.draw(SCREEN)

        if len(players) == 0:
            break

        if len(obstacles) == 0:
            rand_int = random.randint(0, 1)
            if rand_int == 0:
                obstacles.append(SmallCactus(
                    SMALL_CACTUS, random.randint(0, 0)))
            elif rand_int == 1:
                obstacles.append(LargeCactus(
                    LARGE_CACTUS, random.randint(0, 0)))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            for i, dinosaur in enumerate(players):
                if dinosaur.rect.colliderect(obstacle.rect):
                    ge[i].fitness -= 1
                    remove(i)

        for i, dinosaur in enumerate(players):
            output = nets[i].activate((dinosaur.rect.y,
                                       distance((dinosaur.rect.x, dinosaur.rect.y),
                                                obstacle.rect.midtop)))
            if output[0] > 0.5 and dinosaur.rect.y == dinosaur.Y_POS:
                dinosaur.dino_jump = True
                dinosaur.dino_run = False
        statistics()
        score()
        clock.tick(30)
        pygame.display.update()


def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
