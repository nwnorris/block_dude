import pygame

class LevelParseError(Exception):

	def __init__(self):
		print("[ERROR] Error parsing level header!")

class InvalidLevelError(Exception):

	def __init__(self):
		print("\t[ERROR] Level does not contain a critical component!")

class BD_Block():

	def __init__(self, type, x, y):
		self.type = type
		self.x = x
		self.y = y

	def toString(self):
		return "[BD_Block {Type=" + str(self.type) + ", X=" + str(self.x) + ", Y=" + str(self.y) + "}]"

	def coordsToString(self):
		return "(" + str(self.x) + ", " + str(self.y) + ")"

	def typeToString(self, type):
		if(type == 1):
			return "BRICK"
		elif(type == 0):
			return "AIR"
		elif(type == 2):
			return "PLAYER"
		elif(type == 3):
			return "WOOD"
		elif(type == 4):
			return "DOOR"

class BD_Level():

	#Initializes instance variables, sets all blocks in level to air
	#A level must be created with a defined id, width, and height
	def __init__(self, id, w, h):
		#Width and height are in blocks, not pixels
		self.id = id
		self.width = w
		self.height = h
		self.contents = []

		self.player_x = 0
		self.player_y = 0
		self.player_direction = -1
		self.player_holding = False

		self.has_player = False

		self.finish = (0, 0)
		self.has_finish = False

		for x in range(0, h):
			row = []
			for j in range(0, w):
				row.append(BD_Block(00, j, x))
			self.contents.append(row)

	#Accessor method for contents
	#Accessed in y,x order so that array structure matches game structure
	def at(self, x, y):
		return self.contents[y][x]

	#Mostly debug function, prints out formatted info about level
	def toString(self):
		return "[BD_Level {ID=" + str(self.id) + ", Width=" + str(self.width) + ", Height=" + str(self.height) + "}]"

	#Add a BD_Block to the level
	def add_block(self, block):
		self.contents[block.y][block.x] = block
		if(block.type == 2):
			self.has_player = True
			self.player_x = block.x
			self.player_y = block.y
		if(block.type == 4):
			self.has_finish = True
			self.finish = (block.x, block.y)
		#print("Added block to level {" + str(self.id) + "} at location " + block.coordsToString())

	#Set a coordinate to air
	def clear(self, spot):
		self.at(spot[0], spot[1]).type = 0

	#Pick up or drop wood block
	def player_interact(self):
		potential_x = self.player_x + self.player_direction
		if(potential_x < self.width and potential_x >= 0):
			if(self.player_holding):
				if(self.at(potential_x, self.player_y).type == 0):
					print("Ok to drop wood at " + str(potential_x) + ", " + str(self.player_y))
					y_coord = self.player_y
					#pseudo-gravity
					while(y_coord - 1 >= 0 and self.at(potential_x, y_coord-1).type == 0):
						y_coord = y_coord - 1
					self.at(potential_x, y_coord).type = 3
					self.at(self.player_x, self.player_y+1).type = 0
					self.player_holding = False
				elif(self.at(potential_x, self.player_y).type == 3 and self.at(potential_x, self.player_y + 1).type  == 0):
					self.clear((self.player_x, self.player_y+1))
					self.at(potential_x, self.player_y + 1).type = 3
					self.player_holding = False
				else:
					print("Can't drop wood!") #Debug
			else:
				if(self.at(potential_x, self.player_y).type == 3 and self.at(potential_x, self.player_y +1).type != 3):
					print("Found wood in direction!")
					self.player_holding = True
					self.at(potential_x, self.player_y).type = 0
					self.at(self.player_x, self.player_y + 1).type = 3
				else:
					print("No wood found to pick up!")

	#Checks if there is air or door directly to the side of the player (facing in a direction)
	#Returns True if there is a valid space to move to, False if potential square is out of bounds or solid.
	def player_safeToMove(self, direction):
		potential_x = self.player_x + direction
		if(potential_x < self.width and potential_x >= 0):	#Check out of bounds
			if(self.at(potential_x, self.player_y).type != 00 and self.at(potential_x, self.player_y).type != 4): #Check block type
					return False
			return True
		else:
			return False

	#Move the player vertically -- only move is a diagonal movement in either direction
	def player_jump(self):
		potential_x = self.player_x + self.player_direction
		potential_y = self.player_y + 1

		if(potential_x < self.width and potential_x >= 0 and potential_y >= 0 and potential_y < self.height):
			potential_type = self.at(potential_x, self.player_y).type
			if((potential_type == 3 or potential_type == 1) and (self.at(potential_x, potential_y).type == 0 or self.at(potential_x, potential_y).type == 4)):
					current_wood = (self.player_x, self.player_y+1)
					current_player = (self.player_x, self.player_y)

					#Can we move both the player and the block?
					if(self.player_holding):
						if(potential_y+1 < self.height):
							if(self.at(potential_x, potential_y + 1).type == 0):
								self.at(potential_x, potential_y +1).type = 3
								self.clear(current_wood)
							else:
								return False
						else:
							return False

					self.clear(current_player)
					self.player_x = self.player_x + self.player_direction
					self.player_y = self.player_y + 1
					self.at(self.player_x, self.player_y).type = 2
					print("Player jumping! New position: " + str(self.player_x) + ", " + str(self.player_y))			

			else:
				return False
							
	#Move the player horizontally
	def player_move(self, direction):
		self.player_direction = direction #This needs to happen regardless of if we actually move
		potential_x = self.player_x + direction
		if(self.player_safeToMove(direction)):
				#Move player and wood (if necessary)
				current_wood = (self.player_x, self.player_y+1)
				current_player = (self.player_x, self.player_y)

				self.at(self.player_x, self.player_y).type = 0
				

				self.player_x = potential_x

				#Gravity
				while(self.player_y-1 >= 0 and self.at(self.player_x, self.player_y-1).type == 0):
					print("Player falling down one block!")
					self.player_y = self.player_y-1

				self.at(self.player_x, self.player_y).type = 2
				

				if(self.player_holding):
					self.at(current_wood[0], current_wood[1]).type = 0
					self.at(self.player_x, self.player_y+1).type = 3

				print("Player is now at " + str(self.player_x) + ", " + str(self.player_y))
 
class BD_StateHandler_Tester():
		def __init__(self, bdsh):
			self.state = bdsh

		def pre(self):
			return self.state.state(0)

		def play(self):
			return self.state.state(1)

		def end(self):
			return self.state.state(2)

		def edit(self):
			return self.state.state(3)

class BD_StateHandler():

	def __init__(self):
		self.current_state = 0
		self.status = BD_StateHandler_Tester(self)

	def stateToString(self, id):
		if(id == 0):
			return "Pre-Level"
		elif(id == 1):
			return "In Level"
		elif(id == 2):
			return "Game Over"
		elif(id == 3):
			return "Editor"

	def stringToState(self, input):
		input = input.lower()
		if(input == "pre-level"):
			return 0
		elif(input == "in level"):
			return 1
		elif(input == "game over"):
			return 2
		elif(input == "editor"):
			return 3

	def notify(self, id):
		print("Changing states from " + self.stateToString(self.current_state) + " to " + self.stateToString(id))
			

	def pre(self):
		self.notify(0)
		self.current_state = 0

	def play(self):
		self.notify(1)
		self.current_state = 1

	def end(self):
		self.notify(2)
		self.current_state = 2

	def edit(self):
		self.notify(3)
		self.current_state = 3

	def state(self, id):
		if(id == self.current_state):
			return True
		return False

	def draw(self, bdgame):
		if(not self.state(2)):
			bdgame.draw()
			if(self.state(0)):
				bdgame.draw_prelevel()
		elif(self.state(2)):
			bdgame.draw_gameover()

class BD_Game():

	#Initializes all necessary class variables, checks for level files, loads and assigns image files
	def __init__(self):

		#Load levels
		counter = 1
		going = True
		levels = []
		while(going):
			try:
				lvl = open("lvl/level" + str(counter) + ".bdl")
				levels.append("lvl/level" + str(counter) + ".bdl")
				lvl.close()
				counter += 1
			except FileNotFoundError:
				going = False
		self.levels = levels
		self.level_max = counter-1

		self.width = 1920
		self.height = 1080

		#Define drawing region
		if(self.width >= self.height):
			self.game_width = int(self.height/1.5)
		else:
			self.game_width = int(self.width/1.5)

		self.block_size = int(self.game_width/12)

		print("Block size: " + str(self.block_size) + "px")
		#Define camera starting position
		self.view_x = 0
		self.view_y = 0

		self.view_threshold = 3.0/12.0

		#Regardless of game size, we will draw it centered on the screen
		self.game_x = int((self.width - self.game_width)/2)
		self.game_y = int((self.height - self.game_width)/2)

		pygame.init()
		self.running = True
		self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)

		self.level_id = 1
		#self.level_max = 1 #DEBUG DO NOT KEEP
		self.level_data = []
		self.has_level = False

		self.state = BD_StateHandler()

		#Load image files and scale them to our game size
		self.wood_img = pygame.transform.scale(pygame.image.load("img/wood.jpg").convert_alpha(), (self.block_size, self.block_size))
		self.bd_img_l = pygame.transform.scale(pygame.image.load("img/block_dude.jpg").convert_alpha(), (self.block_size, self.block_size))
		self.bd_img_r = pygame.transform.flip(self.bd_img_l, True, False)
		self.door_img = pygame.transform.scale(pygame.image.load("img/door.jpg").convert_alpha(), (self.block_size, self.block_size))
		self.has_img = True
		self.brick_img = pygame.Surface((self.block_size, self.block_size))
		self.brick_img.fill((0,0,0))

		#Initialize timer
		self.clock = pygame.time.Clock()

		self.run()

	#Load a new level into memory
	#Effectively resets a level
	def new_level(self):
		#Parse data from level file

		level_fname = "level" + str(self.level_id) + ".bdl"
		print("Attempting to load level " + str(self.level_id) + " from file \'" + level_fname + "\'")

		level_file = open(self.levels[self.level_id-1])

		lines = level_file.readlines()
		lvl_info = lines[0]

		#Make sure our level info header is intact
		if(len(lvl_info) == 9):
			#Strip percent signs and get id, width, & height
			lvl_info = lvl_info[1:7]
			lvl_id = int(lvl_info[0:2])
			lvl_width = int(lvl_info[2:4])
			lvl_height = int(lvl_info[4:])
			lines.pop(0) #We've parsed the data line

			lvl = BD_Level(lvl_id, lvl_width, lvl_height)

			print(lvl.toString())

			#Parse block info
			for line in lines:
				#Check for bad data
				if(len(line) != 6 and line[6:] != "\n"):
					print("[Error] Invalid format in file \'" + level_fname + "\'")
					print("[Error] (" + line + ")")
				else:
					#Parse block from data line
					x = line
					if(len(x) > 6):
						x = x[0:6]
					block_type = int(x[0:2])
					block_x = int(x[2:4])
					block_y = int(x[4:])

					block = BD_Block(block_type, block_x, block_y)
					lvl.add_block(block)

					print(block.toString())

			if(not lvl.has_player):
				raise InvalidLevelError
			if(not lvl.has_finish):
				raise InvalidLevelError

			for row in reversed(lvl.contents):
				r = ""
				for block in row:
					if(block == None):
						r = r + "[L]"
					else:
						r = r + "[" + str(block.type) + "]"
				print(r)

			self.level = lvl
			self.has_level = True
			self.state.pre()
		else:
			print(lvl_info)
			raise LevelParseError

	#Main game loop
	#Get user input, manage game state, adjust viewport as necessary
	def run(self):
		self.click_coords = (0,0)
		while(self.running):

			if(not self.has_level and not self.state.status.end()):
				self.new_level()

			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					self.running = False
				elif e.type == pygame.KEYDOWN:

					key = pygame.key.name(e.key)
					if key == "escape":
						if((self.state.status.pre() and self.has_level) or self.state.status.end()):
							self.running = False
						else:
							self.has_level = False
							self.state.pre()
					if (key == "j" or key == "a") and not self.state.status.pre():
						#Move left
						self.level.player_move(-1)
					if (key == "l" or key == "d") and not self.state.status.pre():
						#Move right
						self.level.player_move(1)
					if (key == "k" or key == "s") and not self.state.status.pre():
						self.level.player_interact()
						#Pickup/drop block
					if (key == "i" or key == "w") and not self.state.status.pre():
						#Move up
						self.level.player_jump()
					if key == "space" and self.state.status.pre():
						if(self.level_id == 1):
							self.clock.tick()
						self.state.play()

				elif e.type == pygame.MOUSEBUTTONDOWN:
					self.click_coords = e.pos
					print("Clicked: " + str(e.pos[0]) + ", " + str(e.pos[1]))

			self.adjust_viewport() #Move viewport when player is near edges

			#Finish a level
			if (not self.state.status.end()):
				if(self.level.player_x == self.level.finish[0] and self.level.player_y == self.level.finish[1]):
					if(self.level_id+1 > self.level_max):
						self.state.end()
						self.clock.tick()
						self.runtime = self.clock.get_time()
					else:
						self.has_level = False
						self.state.pre()
						self.level_id = self.level_id + 1

			self.screen.fill((255, 255, 255)) #Clear screen
			#pygame.draw.circle(self.screen, (0, 255, 0), self.click_coords, 5)

			self.state.draw(self)

			pygame.display.flip()

	def adjust_viewport(self):
		#Adjust viewport if necessary
		#Compare relative player coordinates to the viewport size
		px = self.level.player_x - self.view_x
		py = self.level.player_y - self.view_y

		if(px <= 3):
			if(self.view_x - 1 >= 0):
				print("Adjusting viewport -1")
				self.view_x = self.view_x - 1
		elif(12-px <= 3):
			if((self.view_x + 1) + 12 <= self.level.width):
				print("Adjusting viewport +1")
				self.view_x = self.view_x + 1

		if(py / float(self.view_y + 12) < self.view_threshold):
			if(self.view_y - 1 >= 0):
				self.view_y = self.view_y - 1
		elif(py / float(self.view_y + 12) >= (1 - self.view_threshold)):
			self.view_y = self.view_y + 1

	#Display the game over screen
	def draw_gameover(self):
		font = pygame.font.SysFont("Arial", 64)
		winText = font.render("You Win!", False, (0, 0, 0))
		timeText = font.render(str(self.runtime/1000) + "s", False, (255, 0, 0))

		winCoords = (int(self.width-winText.get_width())/2, int((self.height-winText.get_height())/2))
		timeCoords = (winText.get_rect().x, winText.get_rect().y + 64)
		self.screen.blit(winText, winCoords)
		self.screen.blit(timeText, timeCoords)

	#Render the pre-level text on the screen
	def draw_prelevel(self):
		w = int(self.game_width/.25)
		h = int(self.game_width * .75)
		
		font = pygame.font.SysFont("Arial", 64)
		level_txt = font.render("Level " + str(self.level.id), False, (0, 0, 0))

		font2 = pygame.font.SysFont("Arial", 32)
		instruction = font2.render("Press spacebar to begin.", False, (0, 0, 0))

		self.screen.blit(level_txt, (self.game_x + self.game_x/4, self.game_y + self.game_width/3))
		self.screen.blit(instruction, (self.game_x + self.game_x/4, self.game_y + self.game_width/3 + 64))
	
	#Draw the current viewport on the screen
	#Viewport is a 12 block by 12 block section of the current level
	def draw(self):
		#Draw self border
		pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(self.game_x, self.game_y, self.game_width, self.game_width), 2)

		xmin = self.view_x
		xmax = self.view_x + 12
		if(xmax >= self.level.width):
			xmax = self.level.width
		ymin = self.view_y
		ymax = self.view_y + 12
		if(ymax >= self.level.height):
			ymax = self.level.height

		for i  in range(self.view_y, self.view_y + 12):
			for j in range(self.view_x, self.view_x + 12):
				block = self.level.at(j, i)
				if(block.type == 0):
					pass
				else:


					block_x = (self.block_size * (block.x - self.view_x)) + self.game_x
					block_y = (self.game_width - (self.block_size * (block.y-self.view_y)) - self.block_size) + self.game_y

					if(self.has_img):
						img = self.brick_img
						if(block.type == 3):
							img = self.wood_img
						elif(block.type == 2):
							if(self.level.player_direction == 1):
								img = self.bd_img_r
							else:
								img = self.bd_img_l
						elif(block.type == 4):
							img = self.door_img

						self.screen.blit(img, (block_x, block_y))
					else:
						block_rect = pygame.Rect(block_x, block_y, self.block_size, self.block_size)

						color = (0, 0, 0)
						if(block.type == 2):
							color = (0, 0, 255)
						elif(block.type == 3):
							color = (0, 255, 255)
						elif(block.type == 4):
							color = (0, 255, 0)
						self.screen.fill(color, rect=block_rect)

game = BD_Game()