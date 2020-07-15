import pygame
import random
import sys
import os
import neat
import math

# Window and Game Properties
GRIDSIZE = 25
GRID_WIDTH = 30
GRID_HEIGHT = 20
WIN_WIDTH = GRID_WIDTH * GRIDSIZE
WIN_HEIGHT = GRID_HEIGHT * GRIDSIZE

UP = (0,-1)
DOWN = (0,1)
LEFT = (-1,0)
RIGHT  = (1,0)

# Quick Functions to Change Directions
def turn_right(direction):
	if direction == LEFT:
		return UP
	elif direction == UP:
		return RIGHT
	elif direction == RIGHT:
		return DOWN
	else:
		return LEFT

def turn_left(direction):
	if direction == LEFT:
		return DOWN
	elif direction == UP:
		return LEFT
	elif direction == RIGHT:
		return UP
	else:
		return RIGHT

# Class to hold snakes and perform snake actions
class Snake(object):
	# All snakes are given random starting position, direction, and color
	def __init__(self):
		self.vel = random.choice([UP, DOWN, LEFT, RIGHT])
		self.positions = [(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))]
		self.length = 1
		self.color = (random.randint(0, 255), random.randint(0, 120), random.randint(0, 255))
		self.alive = True
		self.moves = 50

	def head_position(self):
		return self.positions[0]

	# Returns a tuple indicating the directions in which the snake can safely move
	def safety(self):
		x, y = self.positions[0]
		dir = self.vel
		dir_r = turn_right(dir)
		dir_l = turn_left(dir)
		vel_x, vel_y = dir
		# Assume all directions are safe
		forward, left, right = 1, 1, 1
		# Mark any direction with a wall or snake body as unsafe
		if x + vel_x < 0 or x + vel_x > GRID_WIDTH - 1 or y + vel_y < 0 or y + vel_y > GRID_HEIGHT - 1:
			forward = 0
		if self.length > 1:
			if (x + vel_x, y + vel_y) in self.positions[1:]:
				forward = 0
		vel_x, vel_y = dir_r
		if x + vel_x < 0 or x + vel_x > GRID_WIDTH - 1 or y + vel_y < 0 or y + vel_y > GRID_HEIGHT - 1:
			right = 0
		if self.length > 1:
			if (x + vel_x, y + vel_y) in self.positions[1:]:
				right = 0
		vel_x, vel_y = dir_l
		if x + vel_x < 0 or x + vel_x > GRID_WIDTH - 1 or y + vel_y < 0 or y + vel_y > GRID_HEIGHT - 1:
			left = 0
		if self.length > 1:
			if (x + vel_x, y + vel_y) in self.positions[1:]:
				left = 0

		return (forward, left, right)

	# Updates snake based on current moving direction and kills snake if it has run into a wall or itself
	def move(self):
		cur_head = self.head_position()
		x, y = self.vel
		new_head = (cur_head[0] + x, cur_head[1] + y)
		self.positions.insert(0, new_head)
		if len(self.positions) > self.length:
			self.positions.pop()
		if self.positions[0][0] < 0 or self.positions[0][0] > GRID_WIDTH - 1 or self.positions[0][1] < 0 or self.positions[0][1] > GRID_HEIGHT - 1:
			self.alive = False
		if self.length > 1 and new_head in self.positions[1:]:
			self.alive = False

	# Returns tuple indicating directions in which snake can see food
	def find_food(self, apple_location):
		# Assume no food can be seen in any direction
		forward, left, right = 0, 0, 0
		x, y = self.head_position()
		ax, ay = apple_location
		# Update direction if food can be seen accordingly
		if self.vel == UP and x == ax and ay > y:
			forward = 1
		elif self.vel == UP and y == ay:
			if x > ax:
				left = 1
			else:
				right = 1
		elif self.vel == DOWN and x == ax and y > ay:
			forward = 1
		elif self.vel == DOWN and y == ay:
			if x > ax:
				right = 1
			else:
				left = 1
		elif self.vel == RIGHT and y == ay and x > ax:
			forward = 1
		elif self.vel == RIGHT and x == ax:
			if y > ay:
				right = 1
			else:
				left = 1
		elif self.vel == LEFT and y == ay and ax > x:
			forward = 1
		elif self.vel == LEFT and x == ax:
			if y > ay:
				left = 1
			else:
				right = 1

		return (forward, left, right)

	def draw(self, surface):
		for part in self.positions:
			pygame.draw.rect(surface, self.color, (part[0]*GRIDSIZE, part[1]*GRIDSIZE, GRIDSIZE, GRIDSIZE))

class Apple(object):
	def __init__(self, positions):
		self.location = (0,0)
		self.color = (255, 0, 0)
		self.random_position(positions)

	# Generates a new, random apple position, ensures that apples are not generated within snake
	def random_position(self, positions):
		self.location = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
		if self.location in positions:
			self.random_position(positions)

	def draw(self, surface):
		pygame.draw.rect(surface, self.color, (self.location[0]*GRIDSIZE, self.location[1]*GRIDSIZE, GRIDSIZE, GRIDSIZE))

def fitness(genomes, config):
	# Game and window initialization
	pygame.init()

	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), 0, 32)

	pygame.display.set_caption("Snake School")

	clock = pygame.time.Clock()
	surface = pygame.Surface(win.get_size())
	surface = surface.convert()

	num_snakes = len(genomes)
	
	# Create snakes and apples
	snakes = [Snake() for i in range(num_snakes)]
	apples = [Apple(snakes[i].head_position()) for i in range(num_snakes)]

	# NN Setup
	nets = []
	ge = []
	for _,g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		g.fitness = 0
		ge.append(g)

	#game loop
	max_rounds = 10000
	round = 0
	alive = True
	while alive and round < max_rounds:
		clock.tick(100)

		surface.fill((0,0,0))
		for i, snake in enumerate(snakes):
			if snakes[i].alive:
				ge[i].fitness += 0.1

				# Feed NN current snake attributes and choose next move
				(forward, left, right) = snakes[i].safety()
				(food_forward, food_left, food_right) = snakes[i].find_food(apples[i].location)
				outputs = nets[i].activate((forward, left, right, food_forward, food_left, food_right))
				max_out = max(outputs)
				new_dir = snakes[i].vel
				if outputs[1] == max_out:
					new_dir = turn_right(new_dir)
				elif outputs[2] == max_out:
					new_dir = turn_left(new_dir)
				snake.vel = new_dir

				# Snakes lose fitness if its new position is further from apple than its previous position
				# Euclidean distances used for comparison
				old_dist = math.sqrt(math.pow(snakes[i].head_position()[0] - apples[i].location[0], 2)
					+ math.pow(snakes[i].head_position()[1] - apples[i].location[1], 2))
				snakes[i].move()
				new_dist = math.sqrt(math.pow(snakes[i].head_position()[0] - apples[i].location[0], 2)
					+ math.pow(snakes[i].head_position()[1] - apples[i].location[1], 2))
				if old_dist > new_dist:
					ge[i].fitness -= 0.15

				# Update game when a snake eats an apple
				if snakes[i].head_position() == apples[i].location:
					ge[i].fitness += 2
					snakes[i].length += 1
					snakes[i].moves += 100
					apples[i].random_position(snakes[i].positions)

				snakes[i].draw(surface)
				apples[i].draw(surface)

				# Snakes have limited moves and will die if they do not eat
				snakes[i].moves -= 1
				if snakes[i].moves < 0:
					snakes[i].alive = False
				if not snakes[i].alive:
					ge[i].fitness -= 1
					snakes.pop(i)
					nets.pop(i)
					ge.pop(i)

		win.blit(surface, (0,0))
		pygame.display.update()

		round += 1
		# Check if any snakes are still alive
		alive = False
		for i, snake in enumerate(snakes):
			if snakes[i].alive:
				alive = True
	
	pygame.quit()

# Create and run NN for n generations
def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
							 neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

	p = neat.Population(config)
	p.add_reporter(neat.StdOutReporter(True))
	p.add_reporter(neat.StatisticsReporter())

	n = 20
	winner = p.run(fitness,20)

if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config.txt")
	run(config_path)