import numpy
import pygame
import sys
import math
import subprocess
import sys

pygame.init()

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

NUM_ROWS= 6
NUM_COLUMNS = 7

SQUARESIZE = 100

width = NUM_COLUMNS * SQUARESIZE
height = (NUM_ROWS+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)

screenWidth = screen.get_width()
screenHeight = screen.get_height()
clock = pygame.time.Clock()
FPS=30

myfont = pygame.font.SysFont("monospace", 75)
smallerFont = pygame.font.SysFont("monospace", 35)

validLocation = False

def createBoard():
	board = numpy.zeros((NUM_ROWS,NUM_COLUMNS))
	return board

def dropPiece(board, row, col, piece):
	board[row][col] = piece

def isValidLocation(board, col):
	return board[NUM_ROWS-1][col] == 0

def getNextOpenRow(board, col):
	for r in range(NUM_ROWS):
		if board[r][col] == 0:
			return r

def printBoard(board):
	print(numpy.flip(board, 0))

def winningMove(board, piece):
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
	for c in range(NUM_COLUMNS):
		for r in range(NUM_ROWS):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(NUM_COLUMNS):
		for r in range(NUM_ROWS):		
			if board[r][c] == 1:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == 2: 
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

def drawMessage(message):
	pass

def drawStartUI():
	menu = True
	selected = 0

	while menu:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					selected = 0
				elif event.key == pygame.K_DOWN:
					selected = 1
				if event.key == pygame.K_RETURN:
					if selected == 0:
						print("Game Started")
						drawBoard(board)
						pygame.display.update()
						game_loop()
					else:
						pygame.quit()
						sys.exit()
		# Main Menu UI
		screen.fill((60,60,60))
		title = myfont.render('Connect Four', True, (255,255,255))
		if selected == 0:
			text_start = smallerFont.render('Player vs Player (Local)', True, RED)
		else:
			text_start = smallerFont.render('Player vs Player (Local)', True, (0,0,0))
		if selected == 1:
			text_quit = smallerFont.render('Quit', True, RED)
		else:
			text_quit = smallerFont.render('Quit', True, (0,0,0))

		title_rect = title.get_rect()
		start_rect = text_start.get_rect()
		quit_rect = text_quit.get_rect()

		# Main Menu Text
		screen.blit(title, (screenWidth/2 - (title_rect[2]/2), 80))
		screen.blit(text_start, (screenWidth/2 - (start_rect[2]/2), 300))
		screen.blit(text_quit, (screenWidth/2 - (quit_rect[2]/2), 360))
		pygame.display.update()
		clock.tick(FPS)
		pygame.display.set_caption("Connect Four - Use arrow keys to select menu option")

def dropPieceAI(board):
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
				pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
				posx = event.pos[0]
				if turn == 0:
					pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
				else: 
					pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
			pygame.display.update()

			if event.type == pygame.MOUSEBUTTONDOWN:
				pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
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
							label = myfont.render("Player 1 wins!!", 1, RED)
							screen.blit(label, (40,10))
							gameOver = True
					else:
						turn -= 1
				# # Ask for Player 2 Input
				else:				
					posx = event.pos[0]
					col = int(math.floor(posx/SQUARESIZE))

					if isValidLocation(board, col):
						print(isValidLocation(board, col)) #debugging
						row = getNextOpenRow(board, col)
						dropPiece(board, row, col, 2)

						if winningMove(board, 2):
							label = myfont.render("Player 2 wins!!", 1, YELLOW)
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