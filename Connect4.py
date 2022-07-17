import sys
import math
import random
import os

try:
	import numpy
	import pygame
	from pygame import gfxdraw
except ImportError:
	import subprocess
	import sys

	def checkRequirements():
		"""Check if the user has the required dependencies, if not, ask to install them"""
		if os.name == 'nt': # Windows
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
			# https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
			subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
			subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
			os.startfile(sys.argv[0]) # Restart game
		sys.exit()

	checkRequirements()

# Colors
BLUE = (23,107,250)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,241,0)
WHITE = (255,255,255)
GRAY = (216,216,216)
GREEN = (0,255,58)

# Constants
NUM_ROWS= 6
NUM_COLUMNS = 7
SQUARESIZE = 87
PADDING = 15
FPS=30

# Sizes
screenWidth = 1024
screenHeight = 768
size = (screenWidth, screenHeight)
RADIUS = int(SQUARESIZE/2 - 5)

# Initialization
pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
validLocation = False
gameOver = False
game_history = []
history_view = 0

# Anti-aliasing (https://stackoverflow.com/questions/23852917/antialiasing-shapes-in-pygame)
def drawCircle(surface, color, pos, radius):
	"""Draw an anti aliased circle"""
	gfxdraw.aacircle(surface, int(pos[0]), int(pos[1]), radius, color)
	gfxdraw.filled_circle(surface, int(pos[0]), int(pos[1]), radius, color)

# Same font for all systems (Because Linux/macOS/Windows ship with different fonts)
def renderText(text, color, fontSize):
	"""Load the needed font and return the rendered text object"""
	rFont = pygame.font.Font('FreeSans.ttf', fontSize)
	rText = rFont.render(text, True, color)
	return rText

def createBoard():
	"""Creates an empty numpy array matrix of NUM_ROWS and NUM_COLUMNS"""
	board = numpy.zeros((NUM_ROWS,NUM_COLUMNS))
	return board

def dropPiece(board, row, col, piece):
	"""Push the players piece to the specified location"""
	game_history.append((piece, row, col))
	board[row][col] = piece

def isValidLocation(board, col):
	"""Returns boolean depending on if the location desired is valid"""
	if col > 6 or col < 0:
		return 0
	return board[NUM_ROWS-1][col] == 0

def getNextOpenRow(board, col):
	"""Return the closest free row"""
	for r in range(NUM_ROWS):
		if board[r][col] == 0:
			return r

# Used for ANSI color codes for logging (Windows 10 and higher / Most Linux terminals / Untested on macOS)
if os.name == 'nt':
	kernel32 = __import__("ctypes").windll.kernel32
	kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
	del kernel32

def printBoard(board):
	"""Prints the array matrix for the user to see their previous game history"""
	for i in reversed(range(NUM_ROWS)):
		for j in range(NUM_COLUMNS):
			if board[i][j] == 1:
				print("\033[0;31m* ", end = '')
			elif board[i][j] == 2:
				print("\033[0;33m* ", end = '')
			else:
				print("\033[0;0m* ", end = '')
		print("\033[1;37m")

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

def tieGame(board):
	"""Detect if the board is full, thus the game is tied"""
	return numpy.all(board)

def drawBoard(board):
	"""Uses pygame's draw functionality to display the current board"""
	# Flush previous screen
	pygame.draw.rect(screen, WHITE, (0,	SQUARESIZE, screenWidth - 250 - PADDING, screenHeight - SQUARESIZE))

	start_vertical = (screenHeight - (SQUARESIZE*NUM_ROWS + PADDING*(NUM_ROWS+2)))
	pygame.draw.rect(screen, BLUE, (PADDING, start_vertical, (NUM_COLUMNS*(PADDING+SQUARESIZE) + PADDING), (NUM_ROWS*(PADDING+SQUARESIZE) + PADDING)), 0, int(RADIUS/2))

	for c in range(NUM_COLUMNS):
		for r in range(NUM_ROWS):
			drawCircle(screen, WHITE, (PADDING + int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), start_vertical + int((r+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2)), RADIUS)
	
	for c in range(NUM_COLUMNS):
		for r in range(NUM_ROWS):
			if board[r][c] == 1:
				drawCircle(screen, RED, (PADDING + int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), screenHeight-int((r+1)*(SQUARESIZE+PADDING)-SQUARESIZE/2+PADDING)-1), RADIUS)
			elif board[r][c] == 2:
				drawCircle(screen, YELLOW, (PADDING + int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), screenHeight-int((r+1)*(SQUARESIZE+PADDING)-SQUARESIZE/2+PADDING)-1), RADIUS)

	drawHistory(board)
	pygame.display.update()

def drawHistory(board):
	"""Displays game history on a side panel"""
	pygame.draw.rect(screen, WHITE, ((screenWidth - 250 - PADDING), PADDING, 250, (screenHeight - (2*PADDING))))
	pygame.draw.rect(screen, GRAY, ((screenWidth - 250 - PADDING), PADDING, 250, (screenHeight - (2*PADDING))), 0, int(RADIUS/2))
	history = pygame.Surface((200, 1200))
	history.fill(GRAY)
	offset = SQUARESIZE*2 + PADDING*3

	miniBoard = pygame.Surface((screenWidth*729/1024, screenHeight*627/768))
	pygame.Surface.fill(miniBoard, GRAY)
	for c in range(NUM_COLUMNS):
		for r in range(NUM_ROWS):
			drawCircle(miniBoard, WHITE, (int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), int((r+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2)), RADIUS)
	for c in range(NUM_COLUMNS):
		for r in range(NUM_ROWS):
			if board[r][c] == 1:
				drawCircle(miniBoard, RED, (int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), (miniBoard.get_height() - int((r+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2)) - 1), RADIUS)
			elif board[r][c] == 2:
				drawCircle(miniBoard, YELLOW, (int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), (miniBoard.get_height() - int((r+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2)) - 1), RADIUS)
	history.blit(renderText("Game History", BLACK, 31 if os.name == 'nt' else 32), (0, 0))
	history.blit(pygame.transform.smoothscale(miniBoard, (176, 150)), (PADDING, 40))
	history.blit(renderText("1    2    3    4    5    6    7", BLACK, 16), (PADDING*1.5, offset - (PADDING*2)))
	history.blit(pygame.transform.rotate(renderText("1    2    3    4    5    6", BLACK, 16), 90), (0, 48))

	for i in range(len(game_history) - (22*history_view)):
		text = renderText("Player " + str(game_history[i + (22*history_view)][0]) + "     Row " + str(game_history[i + (22*history_view)][1] + 1) + " Column " + str(game_history[i + (22*history_view)][2] + 1), BLACK, 16)
		location = pygame.Rect(0, history.get_height()*i/56 + offset, history.get_width() - 2*PADDING, history.get_height()/56)
		history.blit(text, (0,(location.centery - (text.get_rect().height/2))))
		drawCircle(history, RED if game_history[i + (22*history_view)][0] == 1 else YELLOW, (67, history.get_height()*i/56 + (text.get_rect().height/2) + offset), 7)

	screen.blit(history, ((screenWidth - 235),PADDING*2), pygame.Rect(0, 0, 200, 692))
	if len(game_history) >= 23:
		screen.blit(renderText("Click for more", BLACK, 20), ((screenWidth - 235),PADDING*2 + 695))
	pygame.display.update()

def drawMessage(message, backgroundColor, foregroundColor, strokeColor, duration):
	"""Uses pygame's rect and label functionality to create a rectangle with the desired message for the user"""
	initial_time = pygame.time.get_ticks()

	while pygame.time.get_ticks() < initial_time + duration:
		bgRect = pygame.Rect((screenWidth/2 - 250), 250, 500, 200)
		pygame.draw.rect(screen, backgroundColor, bgRect, 0, 10)
		mText = renderText(message, foregroundColor, 55)
		rText = mText.get_rect()
		mText2 = renderText(message, strokeColor, 55)
		rText2 = mText2.get_rect()

		screen.blit(mText2, (screenWidth/2 - (rText2[2]/2) + 3, 323))
		screen.blit(mText, (screenWidth/2 - (rText[2]/2), 320))
		
		pygame.display.update()

def drawStartUI(board, gameOver):
	"""Draws main menu UI"""
	menu = True
	game_history.clear()

	# Flush previous screen
	pygame.Surface.fill(screen, WHITE)

	while menu:
		mouse_pos = pygame.mouse.get_pos()
		screen.fill(WHITE)
		
		#Text Initializer
		text_start = renderText("Player vs Player (Local)", BLACK, 35)
		text_quit = renderText("Quit", BLACK, 35)
		p_v_AI = renderText("Player vs AI", BLACK, 35)
		AI_easy = renderText("Easy", BLACK, 35)
		AI_med = renderText("Medium", BLACK, 35)
		AI_hard = renderText("Hard", BLACK, 35)
		title = renderText("Connect 4", BLACK, 120)

		#Main Menu Rectangles
		background_rect = pygame.Rect(screenWidth*131/1280, screenHeight*433/768, screenWidth*103/128, screenHeight*5/12)
		player_v_player_l_rect = pygame.Rect(screenWidth*131/512, screenHeight*438/768, screenWidth/2, screenHeight*25/256)
		player_v_ai_background_rect = pygame.Rect(screenWidth*131/512, screenHeight*518/768, screenWidth/2, screenHeight*50/256)
		player_v_player_o_rect = pygame.Rect(screenWidth*131/512, screenHeight*673/768, screenWidth/2, screenHeight*25/256)
		ai_easy_rect = pygame.Rect(screenWidth*285/1024, screenHeight*578/768, screenWidth*135/1024, screenHeight*25/256)
		ai_med_rect = pygame.Rect(screenWidth*450/1024, screenHeight*578/768, screenWidth*135/1024, screenHeight*25/256)
		ai_hard_rect = pygame.Rect(screenWidth*615/1024, screenHeight*578/768, screenWidth*135/1024, screenHeight*25/256)

		pygame.draw.rect(screen, YELLOW, background_rect, 0, 10) # Background
		pygame.draw.rect(screen, RED, player_v_player_l_rect, 0, 10) # Player vs. Player (local)
		pygame.draw.rect(screen, GREEN, player_v_ai_background_rect, 0, 10) # Player vs. AI background
		pygame.draw.rect(screen, BLUE, player_v_player_o_rect, 0, 10) # Player vs. Player (online)
		pygame.draw.rect(screen, GRAY, ai_easy_rect, 0, 10) # AI easy
		pygame.draw.rect(screen, GRAY, ai_med_rect, 0, 10) # AI medium
		pygame.draw.rect(screen, GRAY, ai_hard_rect, 0, 10) # AI hard

		#Hover & Click Events
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if mouse_pos[0] in range(player_v_player_l_rect.left, player_v_player_l_rect.right) and mouse_pos[1] in range(player_v_player_l_rect.top, player_v_player_l_rect.bottom):
					if gameOver:
						gameOver = False
					board = createBoard()
					drawBoard(board)
					gameLoop(gameOver, board, 0)
				elif mouse_pos[0] in range(ai_easy_rect.left, ai_easy_rect.right) and mouse_pos[1] in range(ai_easy_rect.top, ai_easy_rect.bottom):
					if gameOver:
						gameOver = False
					board = createBoard()
					drawBoard(board)
					gameLoop(gameOver, board, 1)
					pass
				elif mouse_pos[0] in range(ai_med_rect.left, ai_med_rect.right) and mouse_pos[1] in range(ai_med_rect.top, ai_med_rect.bottom):
					if gameOver:
						gameOver = False
					board = createBoard()
					drawBoard(board)
					gameLoop(gameOver, board, 2)
					pass
				elif mouse_pos[0] in range(ai_hard_rect.left, ai_hard_rect.right) and mouse_pos[1] in range(ai_hard_rect.top, ai_hard_rect.bottom):
					if gameOver:
						gameOver = False
					board = createBoard()
					drawBoard(board)
					gameLoop(gameOver, board, 3)
					pass
				elif mouse_pos[0] in range(player_v_player_o_rect.left, player_v_player_o_rect.right) and mouse_pos[1] in range(player_v_player_o_rect.top, player_v_player_o_rect.bottom):
					pygame.quit()
					sys.exit()

		if mouse_pos[0] in range(player_v_player_l_rect.left, player_v_player_l_rect.right) and mouse_pos[1] in range(player_v_player_l_rect.top, player_v_player_l_rect.bottom):
			text_start = renderText("Player vs Player (Local)", WHITE, 35)
		else:
			text_start = renderText("Player vs Player (Local)", BLACK, 35)
		if mouse_pos[0] in range(ai_easy_rect.left, ai_easy_rect.right) and mouse_pos[1] in range(ai_easy_rect.top, ai_easy_rect.bottom):
			AI_easy = renderText("Easy", (0x00,0xA0,0x00), 35)
		else:
			AI_easy = renderText("Easy", BLACK, 35)
		if mouse_pos[0] in range(ai_med_rect.left, ai_med_rect.right) and mouse_pos[1] in range(ai_med_rect.top, ai_med_rect.bottom):
			AI_med = renderText("Medium", (0xC7,0xC7,0x00), 35)
		else:
			AI_med = renderText("Medium", BLACK, 35)
		if mouse_pos[0] in range(ai_hard_rect.left, ai_hard_rect.right) and mouse_pos[1] in range(ai_hard_rect.top, ai_hard_rect.bottom):
			AI_hard = renderText("Hard", RED, 35)
		else:
			AI_hard = renderText("Hard", BLACK, 35)
		if mouse_pos[0] in range(player_v_player_o_rect.left, player_v_player_o_rect.right) and mouse_pos[1] in range(player_v_player_o_rect.top, player_v_player_o_rect.bottom):
			text_quit = renderText("Quit", WHITE, 35)
		else:
			text_quit = renderText("Quit", BLACK, 35)

		# Connect 4 Logo
		if not numpy.any(board):
			board = [
				[1, 2, 2, 1, 2, 0, 0],
				[0, 1, 2, 1, 1, 0, 0],
				[0, 0, 1, 2, 0, 0, 0],
				[0, 0, 0, 1, 0, 0, 0],
				[0, 0, 0, 0, 0, 0, 0],
				[0, 0, 0, 0, 0, 0, 0],
				[0, 0, 0, 0, 0, 0, 0],
			]

		logo = pygame.Surface((screenWidth*729/1024, screenHeight*627/768))
		pygame.Surface.fill(logo, WHITE)
		pygame.draw.rect(logo, BLUE, (0, 0, logo.get_width(), logo.get_height()), 0, int(RADIUS/2))

		for c in range(NUM_COLUMNS):
			for r in range(NUM_ROWS):
				drawCircle(logo, WHITE, (int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), int((r+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2)), RADIUS)

		for c in range(NUM_COLUMNS):
			for r in range(NUM_ROWS):
				if board[r][c] == 1:
					drawCircle(logo, RED, (int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), (logo.get_height() - int((r+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2)) - 1), RADIUS)
				elif board[r][c] == 2:
					drawCircle(logo, YELLOW, (int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), (logo.get_height() - int((r+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2)) - 1), RADIUS)
		pygame.draw.rect(logo, GRAY, (SQUARESIZE, SQUARESIZE, logo.get_width() - (2*SQUARESIZE), (2*SQUARESIZE)), 0, int(RADIUS/2))

		# Main Menu Text
		screen.blit(text_start, ((player_v_player_l_rect.centerx - (text_start.get_rect().width/2)), (player_v_player_l_rect.centery - (text_start.get_rect().height/2))))
		screen.blit(p_v_AI, ((player_v_ai_background_rect.centerx - (p_v_AI.get_rect().width/2)), (player_v_ai_background_rect.y + (p_v_AI.get_rect().height/4))))
		screen.blit(AI_easy, ((ai_easy_rect.centerx - (AI_easy.get_rect().width/2)), (ai_easy_rect.centery - (AI_easy.get_rect().height/2))))
		screen.blit(AI_med, ((ai_med_rect.centerx - (AI_med.get_rect().width/2)), (ai_med_rect.centery - (AI_med.get_rect().height/2))))
		screen.blit(AI_hard, ((ai_hard_rect.centerx - (AI_hard.get_rect().width/2)), (ai_hard_rect.centery - (AI_hard.get_rect().height/2))))
		screen.blit(text_quit, ((player_v_player_o_rect.centerx - (text_quit.get_rect().width/2)), (player_v_player_o_rect.centery - (text_quit.get_rect().height/2))))
		logo.blit(title, ((logo.get_width() - title.get_rect().width)/2, (SQUARESIZE*4 - title.get_rect().height)/2))
		screen.blit(pygame.transform.smoothscale(logo, (468, 403)), (screenWidth/2 - int(468/2), PADDING))
		pygame.display.update()
		clock.tick(FPS)
		pygame.display.set_caption("Connect Four")

def dropPieceAI(difficulty, board, piece):
	"""Select the best move determined on the AI difficulty"""
	if (difficulty == 1): # Easy
		col = random.randint(0,6)
		while (not isValidLocation(board,col)):
			col = random.randint(0,6)
		dropPiece(board, getNextOpenRow(board, col), col, piece)

	elif (difficulty == 2): # Medium

		# Pick a random location sometimes even when a win should be given
		if (random.randint(0,1)):
			c = random.randint(0,6)
			while (not isValidLocation(board,c)):
				c = random.randint(0,6)
			dropPiece(board, getNextOpenRow(board, c), c, piece)
			return

		# Check horizontal locations
		for c in range(NUM_COLUMNS-3):
			for r in range(NUM_ROWS):
				if board[r][c] == 0 and getNextOpenRow(board, c) == r and board[r][c+1] == 1 and board[r][c+2] == 1 and board[r][c+3] == 1:
					dropPiece(board, r, c, piece)
					return
				elif board[r][c] == 1 and board[r][c+1] == 0 and getNextOpenRow(board, c+1) == r and board[r][c+2] == 1 and board[r][c+3] == 1:
					dropPiece(board, r, c+1, piece)
					return
				elif board[r][c] == 1 and board[r][c+1] == 1 and board[r][c+2] == 0 and getNextOpenRow(board, c+2) == r and board[r][c+3] == 1:
					dropPiece(board, r, c+2, piece)
					return
				elif board[r][c] == 1 and board[r][c+1] == 1 and board[r][c+2] == 1 and board[r][c+3] == 0 and getNextOpenRow(board, c+3) == r:
					dropPiece(board, r, c+3, piece)
					return

		# Check vertical locations
		for c in range(NUM_COLUMNS):
			for r in range(NUM_ROWS-3):
				if board[r][c] == 1 and board[r+1][c] == 1 and board[r+2][c] == 1 and board[r+3][c] == 0:
					dropPiece(board, r+3, c, piece)
					return

		# Check diaganols
		for c in range(NUM_COLUMNS-3):
			for r in range(NUM_ROWS-3):
				if board[r][c] == 0 and getNextOpenRow(board, c) == r and board[r+1][c+1] == 1 and board[r+2][c+2] == 1 and board[r+3][c+3] == 1:
					dropPiece(board, r, c, piece)
					return
				elif board[r][c] == 1 and board[r+1][c+1] == 0 and getNextOpenRow(board, c+1) == r+1 and board[r+2][c+2] == 1 and board[r+3][c+3] == 1:
					dropPiece(board, r+1, c+1, piece)
					return
				elif board[r][c] == 1 and board[r+1][c+1] == 1 and board[r+2][c+2] == 0 and getNextOpenRow(board, c+2) == r+2 and board[r+3][c+3] == 1:
					dropPiece(board, r+2, c+2, piece)
					return
				elif board[r][c] == 1 and board[r+1][c+1] == 1 and board[r+2][c+2] == 1 and board[r+3][c+3] == 0 and getNextOpenRow(board, c+3) == r+3:
					dropPiece(board, r+3, c+3, piece)
					return

		# If not blocking opponent, pick a random location
		c = random.randint(0,6)
		while (not isValidLocation(board,c)):
			c = random.randint(0,6)
		dropPiece(board, getNextOpenRow(board, c), c, piece)

	elif (difficulty == 3): # Hard
		pass

def gameLoop(gameOver, board, mode):
	global history_view
	turn = 0
	currentWinner = 0
	
	while not gameOver:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

			if event.type == pygame.MOUSEMOTION:
				posx = event.pos[0]

				if ((posx > screenWidth - 250 - PADDING - (SQUARESIZE*3/4))):
					posx = screenWidth - 250 - PADDING - (SQUARESIZE*3/4)
				elif (posx < SQUARESIZE*3/4):
					posx = SQUARESIZE*3/4

				pygame.draw.rect(screen, WHITE, (0,0, screenWidth - 250 - PADDING, SQUARESIZE))
				if turn == 0:
					drawCircle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
				else: 
					drawCircle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)

			if event.type == pygame.MOUSEBUTTONDOWN:
				posx = event.pos[0]
				if (posx >= (screenWidth - 250 - PADDING)) and (len(game_history) >= 23): # Clicked on right side of screen
					history_view = 0 if history_view else 1
					drawBoard(board)
				elif (posx > PADDING and posx < (screenWidth - 250 - PADDING)):
					col = int(math.floor((posx-PADDING)/(SQUARESIZE+PADDING)))
					if isValidLocation(board, col):
						pygame.draw.rect(screen, WHITE, (0,0, screenWidth, SQUARESIZE))
						row = getNextOpenRow(board, col)
						dropPiece(board, row, col, turn+1)
						if winningMove(board, turn+1):
							currentWinner = turn+1
							gameOver = True
						elif tieGame(board):
							currentWinner = 3
							gameOver = True
						print("--- TURN " + str(len(game_history)) + " ---")
						printBoard(board)
						drawBoard(board)
					else:
						drawMessage("Invalid Move!", GREEN, BLACK, GRAY, 800)
						drawBoard(board)
						turn -= 1

					turn += 1
					turn = turn % 2

		if mode and turn: #aka if AI
			dropPieceAI(mode, board, turn+1)
			print("--- TURN " + str(len(game_history)) + " ---")
			printBoard(board)
			drawBoard(board)
			if winningMove(board, turn+1):
				currentWinner = turn+1
				gameOver = True
			elif tieGame(board):
				currentWinner = 3
				gameOver = True
			turn += 1
			turn = turn % 2

		pygame.display.update()

	if currentWinner == 1:
		drawMessage("PLAYER 1 WINS!!", RED, WHITE, BLACK, 2000)
	elif currentWinner == 2:
		drawMessage("PLAYER 2 WINS!!", YELLOW, BLACK, GRAY, 2000)
	elif currentWinner == 3:
		drawMessage("TIE GAME!!", GREEN, BLACK, GRAY, 2000)
	else:
		drawMessage("THIS SHOULD NEVER HAPPEN", RED, WHITE, BLACK, 5000)

	results_screen = 1
	drawBoard(board)
	screen.blit(renderText("Press any key to return to the menu", BLACK, 47 if os.name == 'nt' else 48), (PADDING/2, SQUARESIZE/2))
	pygame.display.update()
	while results_screen:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				posx = event.pos[0]
				if (posx >= (screenWidth - 250 - PADDING)) and (len(game_history) >= 23): # Clicked on right side of screen
					history_view = 0 if history_view else 1
					drawBoard(board)
					screen.blit(renderText("Press any key to return to the menu", BLACK, 47 if os.name == 'nt' else 48), (PADDING/2, SQUARESIZE/2))
					pygame.display.update()
			if event.type == pygame.KEYDOWN:
				results_screen = 0

	history_view = 0
	drawStartUI(board, gameOver)

drawStartUI(createBoard(), gameOver)
