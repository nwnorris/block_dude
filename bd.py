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

	def at(self, x, y):
		return self.contents[y][x]

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

	def clear(self, spot):
		self.at(spot[0], spot[1]).type = 0

	def player_interact(self):
		potential_x = self.player_x + self.player_direction
		if(potential_x < self.width and potential_x >= 0):
			if(self.player_holding):
				if(self.at(self.player_x + self.player_direction, self.player_y).type == 0):
					print("Ok to drop wood at " + str(self.player_x + self.player_direction) + ", " + str(self.player_y))
					y_coord = self.player_y
					while(y_coord - 1 >= 0 and self.at(potential_x, y_coord-1).type == 0):
						y_coord = y_coord - 1
					self.at(self.player_x + self.player_direction, y_coord).type = 3
					self.at(self.player_x, self.player_y+1).type = 0
					self.player_holding = False
				elif(self.at(self.player_x + self.player_direction, self.player_y).type == 3):
					self.clear((self.player_x, self.player_y+1))
					self.at(self.player_x + self.player_direction, self.player_y + 1).type = 3
					self.player_holding = False
				else:
					print("Can't drop wood!")
					#Todo: gravity
			else:
				if(self.at(self.player_x + self.player_direction, self.player_y).type == 3 and self.at(self.player_x + self.player_direction, self.player_y +1).type != 3):
					print("Found wood in direction!")
					self.player_holding = True
					self.at(self.player_x + self.player_direction, self.player_y).type = 0
					self.at(self.player_x, self.player_y + 1).type = 3
				else:
					print("No wood found to pick up!")

	def player_safeToMove(self, direction):
		potential_x = self.player_x + direction
		if(potential_x < self.width and potential_x >= 0):
			if(self.player_holding):
				if(self.at(self.player_x+direction, self.player_y).type != 00 and self.at(potential_x, self.player_y).type != 4):
					print("Found non-air block at " + str(potential_x) + ", " + str(self.player_y))
					return False
				return True
			elif(self.at(potential_x, self.player_y).type != 00 and self.at(potential_x, self.player_y).type != 4):
					return False
			return True
		else:
			return False

	def player_jump(self):
		potential_x = self.player_x + self.player_direction
		potential_y = self.player_y + 1

		if(potential_x < self.width and potential_x >= 0 and potential_y >= 0 and potential_y < self.height):
			if(self.at(potential_x, self.player_y).type == 3 or self.at(potential_x, self.player_y).type == 1):

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
 


class BD_Game():

	def __init__(self):
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
		self.level_data = []
		self.has_level = False

		self.pre_level = True #Pre-level information mode

		self.run()

	def new_level(self):
		#Parse data from level file

		level_fname = "level" + str(self.level_id) + ".bdl"
		print("Attempting to load level " + str(self.level_id) + " from file \'" + level_fname + "\'")
		level_file = open(level_fname)

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
			self.pre_level = True
		else:
			print(lvl_info)
			raise LevelParseError

	def run(self):
		self.click_coords = (0,0)
		while(self.running):

			if(not self.has_level):
				self.new_level()

			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					self.running = False
				elif e.type == pygame.KEYDOWN:
					key = pygame.key.name(e.key)
					if key == "escape":
						self.running = False
					if key == "j" and not self.pre_level:
						#Move left
						self.level.player_move(-1)
					if key == "l" and not self.pre_level:
						#Move right
						self.level.player_move(1)
					if key == "k" and not self.pre_level:
						self.level.player_interact()
						#Pickup/drop block
					if key == "i" and not self.pre_level:
						#Move up
						self.level.player_jump()
					if key == "space" and self.pre_level:
						self.pre_level = False


				elif e.type == pygame.MOUSEBUTTONDOWN:
					self.click_coords = e.pos
					print("Clicked: " + str(e.pos[0]) + ", " + str(e.pos[1]))

			#Adjust viewport if necessary

			#Compare relative player coordinates to the viewport size
			px = self.level.player_x - self.view_x
			py = self.level.player_y - self.view_y

			if(px <= 2):
				if(self.view_x - 1 >= 0):
					print("Adjusting viewport -1")
					self.view_x = self.view_x - 1
			elif(12-px <= 2):
				if((self.view_x + 1) + 12 <= self.level.width):
					print("Adjusting viewport +1")
					self.view_x = self.view_x + 1

			if(py / float(self.view_y + 12) < self.view_threshold):
				if(self.view_y - 1 >= 0):
					self.view_y = self.view_y - 1
			elif(py / float(self.view_y + 12) >= (1 - self.view_threshold)):
				self.view_y = self.view_y + 1


			if(self.level.player_x == self.level.finish[0] and self.level.player_y == self.level.finish[1]):
				self.has_level = False
				self.level_id = self.level_id + 1

			self.screen.fill((255, 255, 255))
			pygame.draw.circle(self.screen, (0, 255, 0), self.click_coords, 5)

			self.draw()

			if(self.pre_level):
				self.draw_header()

			pygame.display.flip()

	def draw_header(self):
		w = int(self.game_width/.25)
		h = int(self.game_width * .75)
		header = pygame.Surface((w, h))

		fullRect = header.get_rect()
		header.fill((0, 0, 0), rect=fullRect)
		header.fill((255, 255, 255), rect=pygame.Rect(fullRect.x + 10, fullRect.y + 10, fullRect.width - 10, fullRect.height - 10))

		font = pygame.font.SysFont("Arial", 64)
		level_txt = font.render("Level " + str(self.level.id), False, (0, 0, 0))

		font2 = pygame.font.SysFont("Arial", 32)
		instruction = font2.render("Press spacebar to begin.", False, (0, 0, 0))

		textpos = (h/2, int((w/.75)/2))
		header.blit(level_txt, textpos)

		self.screen.blit(level_txt, (self.game_x + self.game_x/4, self.game_y + self.game_width/3))
		self.screen.blit(instruction, (self.game_x + self.game_x/4, self.game_y + self.game_width/3 + 64))
	
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
