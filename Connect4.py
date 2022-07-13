import sys
import math

try:
	import numpy
	import pygame
except ImportError:
	import subprocess
	import sys
	import os

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

def renderText(text, color, fontSize, font="Helvetica"):
    rFont = pygame.font.SysFont(font, fontSize)
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
	if col > 7:
		return 0
	return board[NUM_ROWS-1][col] == 0

def getNextOpenRow(board, col):
	"""Return the closest free row"""
	for r in range(NUM_ROWS):
		if board[r][col] == 0:
			return r

def printBoard(board):
	"""Prints the array matrix for the user to see their previous game history"""
	print(numpy.flip(board, 0))

board = createBoard()
printBoard(board)

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

	# Flush previous screen
	pygame.Surface.fill(screen, WHITE)

	start_vertical = (screenHeight - (SQUARESIZE*NUM_ROWS + PADDING*(NUM_ROWS+2)))

	pygame.draw.rect(screen, BLUE, (PADDING, start_vertical, (NUM_COLUMNS*(PADDING+SQUARESIZE) + PADDING), (NUM_ROWS*(PADDING+SQUARESIZE) + PADDING)), 0, int(RADIUS/2))

	for c in range(NUM_COLUMNS):
		for r in range(NUM_ROWS):
			pygame.draw.circle(screen, WHITE, (PADDING + int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), start_vertical + int((r+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2)), RADIUS)
	
	for c in range(NUM_COLUMNS):
		for r in range(NUM_ROWS):
			if board[r][c] == 1:
				pygame.draw.circle(screen, RED, (PADDING + int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), screenHeight-int((r+1)*(SQUARESIZE+PADDING)-SQUARESIZE/2+PADDING)-1), RADIUS)
			elif board[r][c] == 2: 
				pygame.draw.circle(screen, YELLOW, (PADDING + int((c+1)*(SQUARESIZE + PADDING) - SQUARESIZE/2), screenHeight-int((r+1)*(SQUARESIZE+PADDING)-SQUARESIZE/2+PADDING)-1), RADIUS)
	drawHistory(board)
	pygame.display.update()

def drawHistory(board):
	"""Displays game history on a side panel"""
	pygame.draw.rect(screen, GRAY, ((screenWidth - 250 - PADDING), PADDING, 250, (screenHeight - (2*PADDING))), 0, int(RADIUS/2))
	history = pygame.Surface((200, 1200))
	history.fill(GRAY)

	for i in range(len(game_history)):
		text = renderText("Player " + str(game_history[i][0]) + "     Row " + str(game_history[i][1] + 1) + " Column " + str(game_history[i][2] + 1), BLACK, 16)
		location = pygame.Rect(0, history.get_height()*i/56, history.get_width() - 2*PADDING, history.get_height()/56)
		history.blit(text, (0,(location.centery - (text.get_rect().height/2))))
		pygame.draw.circle(history, RED if game_history[i][0] == 1 else YELLOW, (67, history.get_height()*i/56 + (text.get_rect().height/2)), 7)

	screen.blit(history, ((screenWidth - 235),PADDING*2), pygame.Rect(0, 0, 200, 700))
	pygame.display.update()

def drawMessage(message, backgroundColor, foregroundColor, strokeColor):
	
	"""Uses pygame's rect and label functionality to create a rectangle with the desired message for the user"""
	time = 3000
	while time:
		bgRect = pygame.Rect((screenWidth/2 - 250), 250, 500, 200)
		pygame.draw.rect(screen, backgroundColor, bgRect, 0, 10)
		mText = renderText(message, foregroundColor, 55)
		rText = mText.get_rect()
		mText2 = renderText(message, strokeColor, 55)
		rText2 = mText2.get_rect()

		screen.blit(mText2, (screenWidth/2 - (rText2[2]/2) + 3, 323))
		screen.blit(mText, (screenWidth/2 - (rText[2]/2), 320))
		
		pygame.display.update()
		time -= 1

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
		logo = pygame.image.load('logo.png')
		text_start = renderText("Player vs Player (Local)", BLACK, 35)
		text_quit = renderText("Quit", BLACK, 35)
		p_v_AI = renderText("Player vs AI", BLACK, 35)
		AI_easy = renderText("Easy", BLACK, 35)
		AI_med = renderText("Medium", BLACK, 35)
		AI_hard = renderText("Hard", BLACK, 35)

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
						board = createBoard()
						print(board)
						drawBoard(board)
						gameOver = False
						game_loop(gameOver, board)
					else:
						drawBoard(board)
						game_loop(gameOver, board)
				elif mouse_pos[0] in range(ai_easy_rect.left, ai_easy_rect.right) and mouse_pos[1] in range(ai_easy_rect.top, ai_easy_rect.bottom):
					#AI EASY GOES HERE
					pass
				elif mouse_pos[0] in range(ai_med_rect.left, ai_med_rect.right) and mouse_pos[1] in range(ai_med_rect.top, ai_med_rect.bottom):
					#AI MED GOES HERE
					pass
				elif mouse_pos[0] in range(ai_hard_rect.left, ai_hard_rect.right) and mouse_pos[1] in range(ai_hard_rect.top, ai_hard_rect.bottom):
					#AI HARD GOES HERE
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

		# Main Menu Text
		screen.blit(text_start, ((player_v_player_l_rect.centerx - (text_start.get_rect().width/2)), (player_v_player_l_rect.centery - (text_start.get_rect().height/2))))
		screen.blit(p_v_AI, ((player_v_ai_background_rect.centerx - (p_v_AI.get_rect().width/2)), (player_v_ai_background_rect.y + (p_v_AI.get_rect().height/4))))
		screen.blit(AI_easy, ((ai_easy_rect.centerx - (AI_easy.get_rect().width/2)), (ai_easy_rect.centery - (AI_easy.get_rect().height/2))))
		screen.blit(AI_med, ((ai_med_rect.centerx - (AI_med.get_rect().width/2)), (ai_med_rect.centery - (AI_med.get_rect().height/2))))
		screen.blit(AI_hard, ((ai_hard_rect.centerx - (AI_hard.get_rect().width/2)), (ai_hard_rect.centery - (AI_hard.get_rect().height/2))))
		screen.blit(text_quit, ((player_v_player_o_rect.centerx - (text_quit.get_rect().width/2)), (player_v_player_o_rect.centery - (text_quit.get_rect().height/2))))
		screen.blit(logo, (screenWidth/2 - int(logo.get_width()/2),0)) # Todo: Fix logo
		pygame.display.update()
		clock.tick(FPS)
		pygame.display.set_caption("Connect Four")

def dropPieceAI(difficulty, board, piece):
	"""Select the best move determined on the AI difficulty"""
	# Function stub --- to be implemented
	# Use dropPiece
	pass

def game_loop(gameOver, board):
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
					pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
				else: 
					pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
			pygame.display.update()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if (posx <= PADDING):
					pass

				pygame.draw.rect(screen, WHITE, (0,0, screenWidth, SQUARESIZE))
				#print(event.pos)
				# Ask for Player 1 Input
				if turn == 0:
					posx = event.pos[0]
					col = int(math.floor((posx-PADDING)/(SQUARESIZE+PADDING)))

					if isValidLocation(board, col):
						print(isValidLocation(board, col)) #debugging
						row = getNextOpenRow(board, col)
						dropPiece(board, row, col, 1)

						if winningMove(board, 1):
							currentWinner = 1
							gameOver = True
					else:
						turn -= 1
				# Ask for Player 2 Input
				else:
					posx = event.pos[0]
					col = int(math.floor((posx-PADDING)/(SQUARESIZE+PADDING)))

					if isValidLocation(board, col):
						print(isValidLocation(board, col)) #debugging
						row = getNextOpenRow(board, col)
						dropPiece(board, row, col, 2)

						if winningMove(board, 2):
							currentWinner = 2
							gameOver = True
					else:
						turn -= 1
				printBoard(board)
				drawBoard(board)

				turn += 1
				turn = turn % 2

				if gameOver:
					if currentWinner == 1:
						drawMessage("PLAYER 1 WINS!!", RED, WHITE, BLACK)
					else:
						drawMessage("PLAYER 2 WINS!!", YELLOW, BLACK, GRAY)
					pygame.time.wait(300) 
					drawStartUI(board, gameOver)
					

drawStartUI(board, gameOver)
