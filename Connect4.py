import sys
import math

try:
	import numpy
	import pygame
except ImportError:
	import subprocess
	import sys
	import os

	# Tbh this has no business being a function due to the way it needs to be called
	def checkRequirements():
		"""Check if the user has the required dependencies, if not, ask to install them"""
		if os.name == 'nt': # Windoze
			import ctypes
			MessageBox = ctypes.windll.user32.MessageBoxW
			result = MessageBox(None, "Missing required modules, do you want to install these?\nThis will take a minute", "Missing Pygame/Numpy", 4)
		else: # Assume POSIX
			print("Install missing numpy/pygame libraries? [(Y)es/No]")
			if input().lower() in {'yes','ye', 'y', ''}:
				result = 6 # Same as MessageBoxW yes on Win32
			else:
				result = 7 # Same as MessageBoxW no on Win32, but it could really be anything

		if result == 6: # User agreed to installation
			print("Please wait a moment while modules are being installed")
			#https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
			subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
			subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
			os.startfile(sys.argv[0]) #Restart game
		sys.exit()

	checkRequirements()


# Colors
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255, 255, 255)
GREY = (216,216,216)

# Constants
NUM_ROWS= 6
NUM_COLUMNS = 7
SQUARESIZE = 100
FPS=30

# Sizes
screenWidth = NUM_COLUMNS * SQUARESIZE
screenHeight = (NUM_ROWS+1) * SQUARESIZE
size = (screenWidth, screenHeight)
RADIUS = int(SQUARESIZE/2 - 5)

# Initialization
pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
# myfont = pygame.font.SysFont("monospace", 75)
# smallerFont = pygame.font.SysFont("monospace", 35)
validLocation = False

def renderText(text, color, fontSize, font="monospace"):
    rFont = pygame.font.SysFont(font, fontSize)
    rText = rFont.render(text, True, color)
    return rText

def createBoard():
	"""Creates an empty numpy array matrix of NUM_ROWS and NUM_COLUMNS"""
	board = numpy.zeros((NUM_ROWS,NUM_COLUMNS))
	return board

def dropPiece(board, row, col, piece):
	"""Push the players piece to the specified location"""
	board[row][col] = piece

def isValidLocation(board, col):
	"""Returns boolean depending on if the location desired is valid"""
	return board[NUM_ROWS-1][col] == 0

def getNextOpenRow(board, col):
	"""Return the closest free row"""
	for r in range(NUM_ROWS):
		if board[r][col] == 0:
			return r

def printBoard(board):
	"""Prints the array matrix for the user to see their previous game history"""
	print(numpy.flip(board, 0))

def winningMove(board, piece):
	"""Checks horizonal/vertical/diaganol positions to determine if there is 4 pieces in a row"""
	# Check horizontal locations for win
	for c in range(NUM_COLUMNS-3):
		for r in range(NUM_ROWS):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(NUM_COLUMNS):
		for r in range(NUM_ROWS-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(NUM_COLUMNS-3):
		for r in range(NUM_ROWS-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(NUM_COLUMNS-3):
		for r in range(3, NUM_ROWS):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

def drawBoard(board):
	"""Uses pygame's draw functionality to display the current board"""
	for c in range(NUM_COLUMNS):
		for r in range(NUM_ROWS):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(NUM_COLUMNS):
		for r in range(NUM_ROWS):		
			if board[r][c] == 1:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), screenHeight-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == 2: 
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), screenHeight-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

def drawMessage(message):
	"""Uses pygame's rect and label functionality to create a rectangle with the desired message for ethe user"""
	# Function stub --- to be implemented
	pass

def drawStartUI():
	"""Draws main menu UI"""
	menu = True

	while menu:
		mouse_pos = pygame.mouse.get_pos()
		screen.fill(WHITE)
		
		logo = pygame.image.load('logo.png')
		text_start = renderText("Player vs Player (Local)", BLACK, 35)
		text_quit = renderText("Quit", BLACK, 35)

		start_rect = text_start.get_rect()
		quit_rect = text_quit.get_rect()
		pygame.draw.rect(screen, GREY, pygame.Rect(90, 295, 510, 55), 0, 10)
		pygame.draw.rect(screen, GREY, pygame.Rect(298, 355, 100, 55), 0, 10)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if mouse_pos[0] in range(90, 600) and mouse_pos[1] in range(295, 350):
					drawBoard(board)
					game_loop()
				elif mouse_pos[0] in range(298, 398) and mouse_pos[1] in range(355, 455):
					pygame.quit()
					sys.exit()
		if mouse_pos[0] in range(90, 600) and mouse_pos[1] in range(295, 350):
			text_start = renderText("Player vs Player (Local)", RED, 35)
		else:
			text_start = renderText("Player vs Player (Local)", BLACK, 35)
		if mouse_pos[0] in range(298, 398) and mouse_pos[1] in range(355, 455):
			text_quit = renderText("Quit", RED, 35)
		else:
			text_quit = renderText("Quit", BLACK, 35)

		# Main Menu Text
		screen.blit(text_start, (screenWidth/2 - (start_rect[2]/2), 300))
		screen.blit(text_quit, (screenWidth/2 - (quit_rect[2]/2), 360))
		screen.blit(logo, (screenWidth/2 - int(logo.get_width()/2),0))
		pygame.display.update()
		clock.tick(FPS)
		pygame.display.set_caption("Connect Four")

def dropPieceAI(difficulty, board, piece):
	"""Select the best move determined on the AI difficulty"""
	# Function stub --- to be implemented
	pass

board = createBoard()
printBoard(board)

def game_loop():
	gameOver = False
	turn = 0
	
	while not gameOver:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

			if event.type == pygame.MOUSEMOTION:
				pygame.draw.rect(screen, BLACK, (0,0, screenWidth, SQUARESIZE))
				posx = event.pos[0]
				if turn == 0:
					pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
				else: 
					pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
			pygame.display.update()

			if event.type == pygame.MOUSEBUTTONDOWN:
				pygame.draw.rect(screen, BLACK, (0,0, screenWidth, SQUARESIZE))
				#print(event.pos)
				# Ask for Player 1 Input
				if turn == 0:
					posx = event.pos[0]
					col = int(math.floor(posx/SQUARESIZE))

					if isValidLocation(board, col):
						print(isValidLocation(board, col)) #debugging
						row = getNextOpenRow(board, col)
						dropPiece(board, row, col, 1)

						if winningMove(board, 1):
							label = renderText("Player 1 wins!!", RED, 75)
							screen.blit(label, (40,10))
							gameOver = True
					else:
						turn -= 1
				# Ask for Player 2 Input
				else:				
					posx = event.pos[0]
					col = int(math.floor(posx/SQUARESIZE))

					if isValidLocation(board, col):
						print(isValidLocation(board, col)) #debugging
						row = getNextOpenRow(board, col)
						dropPiece(board, row, col, 2)

						if winningMove(board, 2):
							label = renderText("Player 2 wins!!", YELLOW, 75)
							screen.blit(label, (40,10))
							gameOver = True
					else:
						turn -= 1
				printBoard(board)
				drawBoard(board)

				turn += 1
				turn = turn % 2

				if gameOver:
					#ADD SHOW GAME HISTORY HERE
					pygame.time.wait(3000) 

drawStartUI()