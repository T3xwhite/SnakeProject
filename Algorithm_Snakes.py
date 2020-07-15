import pygame
import random
import sys

GRIDSIZE = 25
GRID_WIDTH = 24
GRID_HEIGHT = 20
WIN_WIDTH = GRID_WIDTH * GRIDSIZE
WIN_HEIGHT = GRID_HEIGHT * GRIDSIZE

UP = (0,-1)
DOWN = (0,1)
LEFT = (-1,0)
RIGHT  = (1,0)

# Class to hold snakes and perform snake actions
class Snake(object):
	# All snakes are given random starting position, direction, and color
	def __init__(self):
		self.vel = random.choice([UP, DOWN, LEFT, RIGHT])
		self.positions = [(random.randint(3, GRID_WIDTH - 4), random.randint(3, GRID_HEIGHT - 4))]
		self.length = 1
		self.color = (random.randint(0, 255), random.randint(0, 120), random.randint(0, 255))
		self.alive = True

	def head_position(self):
		return self.positions[0]

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
		if self.length > 2 and new_head in self.positions[2:]:
			self.alive = False

	# Handles key input in order for human to control snake
	def handle_keys(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				opp_vel = (-1 * self.vel[0], -1 * self.vel[1])
				new_vel = UP
				if event.key == pygame.K_UP:
					new_vel = UP
				elif event.key == pygame.K_DOWN:
					new_vel = DOWN
				elif event.key == pygame.K_LEFT:
					new_vel = LEFT
				elif event.key == pygame.K_RIGHT:
					new_vel = RIGHT
				else:
					new_vel = self.vel
				if not new_vel == opp_vel:
					return new_vel
		return self.vel


	def draw(self, surface):
		for part in self.positions:
			pygame.draw.rect(surface, self.color, (part[0]*GRIDSIZE, part[1]*GRIDSIZE, GRIDSIZE, GRIDSIZE))

	# Returns list of adjacent coordinates to coord, taking into account walls
	def get_adjacent(self, coord):
		x, y = coord
		adjacent = []
		if x > 0:
			adjacent.append((x - 1, y))
		if y > 0:
			adjacent.append((x, y - 1))
		if x < GRID_WIDTH - 1:
			adjacent.append((x + 1, y))
		if y < GRID_HEIGHT - 1:
			adjacent.append((x, y + 1))
		return adjacent

	# Takes a predecessor list and end location and contructs path from snake's current location to end
	def backtrace_and_convert(self, previous, end):
		path = []
		current = end
		while not current == self.head_position():
			prev = previous[current]
			x1, y1 = prev
			x2, y2 = current
			move = (x2 - x1, y2 - y1)
			path.append(move)
			current = prev

		path.reverse()
		return path

	# Does a breadth first search for a path from the snake's current position to the apple
	# Path generated will always avoid walls and the snake itself
	# If no such path exists, an empty path will be returned
	def BFS(self, apple_location):
		previous = {}
		visited = []
		queue = []
		queue.append(self.head_position())
		visited.append(self.head_position())

		while queue:
			current = queue.pop(0)
			for next in self.get_adjacent(current):
				if next not in self.positions and next not in visited:
					visited.append(next)
					queue.append(next)
					previous[next] = current
					if next == apple_location:
						return self.backtrace_and_convert(previous, apple_location)
		return []

# Class which manages apples and their locations
class Apple(object):
	def __init__(self):
		self.location = (0,0)
		self.color = (255, 0, 0)
		self.random_position([])

	def random_position(self, positions):
		self.location = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
		if self.location in positions:
			self.random_position(positions)

	def draw(self, surface):
		pygame.draw.rect(surface, self.color, (self.location[0]*GRIDSIZE, self.location[1]*GRIDSIZE, GRIDSIZE, GRIDSIZE))

# Class which manages a snake's algorithm used to determine its next move
class Algorithm(object):
	def __init__(self, direction, snake_location, apple_location, alg_type):
		self.direction = direction
		self.snake_location = snake_location
		self.apple_location = apple_location
		self.alg_type = alg_type
		self.path = []

	def get_type(self):
		return self.alg_type

	def update_snake(self, snake_location):
		self.snake_location = snake_location

	def update_apple(self, apple_location):
		self.apple_location = apple_location

	def update_direction(self, direction):
		self.direction = direction

	def update_path(self, path):
		self.path = path

	# Determines next move based solely on fastest way to get to the apple
	def SP_move(self):
		if self.apple_location[0] > self.snake_location[0]:
			return RIGHT
		elif self.apple_location[0] < self.snake_location[0]:
			return LEFT
		elif self.apple_location[1] < self.snake_location[1]:
			return UP
		else:
			return DOWN

	# Chooses next move based on algorithm type
	def next_move(self):
		# BFS Move
		if self.get_type() == 2:
			if not self.path:
				if self.direction == LEFT:
					return DOWN
				else:
					return RIGHT
			next = self.path.pop(0)
			return next

		# Shortest Path Move
		desired = self.SP_move()
		opp_desired = (desired[0] * -1, desired[1] * -1)
		if self.direction == opp_desired:
			if desired == UP or desired == DOWN:
				return RIGHT
			else:
				return UP
		else:
			return desired


def main():
	#game and window initialization
	pygame.init()

	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), 0, 32)

	pygame.display.set_caption("Snake is Gonna Be Great")

	clock = pygame.time.Clock()
	surface = pygame.Surface(win.get_size())
	surface = surface.convert()

	myfont = pygame.font.SysFont("monospace", 16)

	# sets number of snakes and which algorithm snakes use
	# algorithm_type (0 - player controlled, 1 - shortest path, 2 - BFS path)
	# NOTE: if using player controlled snake, num_snakes must be 1
	num_snakes = 10
	algorithm_type = 2

	#create snakes and apples
	snakes = [Snake() for i in range(num_snakes)]
	apples = [Apple() for i in range(num_snakes)]
	algorithms = [Algorithm(snakes[i].vel, snakes[i].head_position(), apples[i].location, algorithm_type) for i in range(num_snakes)]

	#game loop
	scores = [0 for i in range(num_snakes)]
	alive = True
	while alive:
		clock.tick(50)

		surface.fill((0,0,0))
		for i in range(num_snakes):
			if snakes[i].alive:
				# Retrieve next move based on algorithm type or human input
				if algorithms[i].get_type() == 0:
					snakes[i].vel = snakes[i].handle_keys()
				else:
					algorithms[i].update_snake(snakes[i].head_position())
					algorithms[i].update_direction(snakes[i].vel)
					if algorithms[i].get_type() == 2 and not algorithms[i].path:
						algorithms[i].update_path(snakes[i].BFS(apples[i].location))
					snakes[i].vel = algorithms[i].next_move()

				snakes[i].move()

				# Update game as necessary when a snake eats an apple
				if snakes[i].head_position() == apples[i].location:
					scores[i] += 1
					snakes[i].length += 1
					apples[i].random_position(snakes[i].positions)
					if not algorithms[i].get_type() == 0:
						algorithms[i].update_apple(apples[i].location)
					if algorithms[i].get_type() == 2:
						algorithms[i].update_snake(snakes[i].head_position())
						algorithms[i].update_path(snakes[i].BFS(apples[i].location))

				snakes[i].draw(surface)
				apples[i].draw(surface)

		win.blit(surface, (0,0))
		if num_snakes == 1:
			text = myfont.render("Score: {0}".format(scores[0]), 2, (255,255,255))
			win.blit(text, (10,10))
		pygame.display.update()

		# Check if any snakes are still alive
		alive = False
		for i in range(num_snakes):
			if snakes[i].alive:
				alive = True
	
	# Once all snakes are dead, print scores and statistics
	print(scores)
	print(max(scores))

	pygame.quit()

main()