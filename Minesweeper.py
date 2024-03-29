"""
Implementation of command-line minesweeper by Kylie Ying

YouTube Kylie Ying: https://www.youtube.com/ycubed 
Twitch KylieYing: https://www.twitch.tv/kylieying 
Twitter @kylieyying: https://twitter.com/kylieyying 
Instagram @kylieyying: https://www.instagram.com/kylieyying/ 
Website: https://www.kylieying.com
Github: https://www.github.com/kying18 
Programmer Beast Mode Spotify playlist: https://open.spotify.com/playlist/4Akns5EUb3gzmlXIdsJkPs?si=qGc4ubKRRYmPHAJAIrCxVQ 

Project specs, files, code all over the place? Start using Backlog for efficient management!! There is a free tier: https://cutt.ly/ehxImv5
"""

import random
import re
import pygame

# lets create a board object to represent the minesweeper game
# this is so that we can just say "create a new board object", or
# "dig here", or "render this game for this object"
class Board:
    def __init__(self, dim_size, num_bombs):
        # let's keep track of these parameters. they'll be helpful later
        self.dim_size = dim_size
        self.num_bombs = num_bombs

        # let's create the board
        # helper function!
        self.board = self.make_new_board() # plant the bombs
        self.assign_values_to_board()

        # initialize a set to keep track of which locations we've uncovered
        # we'll save (row,col) tuples into this set 
        # if we dig at 0, 0, then self.dug = {(0,0)}

    def make_new_board(self):
        # construct a new board based on the dim size and num bombs
        # we should construct the list of lists here (or whatever representation you prefer,
        # but since we have a 2-D board, list of lists is most natural)

        # generate a new board
        board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        # this creates an array like this:
        # [[None, None, ..., None],
        #  [None, None, ..., None],
        #  [...                  ],
        #  [None, None, ..., None]]
        # we can see how this represents a board!

        # plant the bombs
        bombs_planted = 0
        while bombs_planted < self.num_bombs:
            loc = random.randint(0, self.dim_size**2 - 1) # return a random integer N such that a <= N <= b
            row = loc // self.dim_size  # we want the number of times dim_size goes into loc to tell us what row to look at
            col = loc % self.dim_size  # we want the remainder to tell us what index in that row to look at

            if board[row][col] == '*':
                # this means we've actually planted a bomb there already so keep going
                continue

            board[row][col] = '*' # plant the bomb
            bombs_planted += 1

        return board

    def assign_values_to_board(self):
        # now that we have the bombs planted, let's assign a number 0-8 for all the empty spaces, which
        # represents how many neighboring bombs there are. we can precompute these and it'll save us some
        # effort checking what's around the board later on :)
        for r in range(self.dim_size):
            for c in range(self.dim_size):
                if self.board[r][c] == '*':
                    # if this is already a bomb, we don't want to calculate anything
                    continue
                self.board[r][c] = self.get_num_neighboring_bombs(r, c)

    def get_num_neighboring_bombs(self, row, col):
        # let's iterate through each of the neighboring positions and sum number of bombs
        # top left: (row-1, col-1)
        # top middle: (row-1, col)
        # top right: (row-1, col+1)
        # left: (row, col-1)
        # right: (row, col+1)
        # bottom left: (row+1, col-1)
        # bottom middle: (row+1, col)
        # bottom right: (row+1, col+1)

        # make sure to not go out of bounds!

        num_neighboring_bombs = 0
        for r in range(max(0, row-1), min(self.dim_size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.dim_size-1, col+1)+1):
                if r == row and c == col:
                    # our original location, don't check
                    continue
                if self.board[r][c] == '*':
                    num_neighboring_bombs += 1

        return num_neighboring_bombs


    def __str__(self):
        # this is a magic function where if you call print on this object,
        # it'll print out what this function returns!
        # return a string that shows the board to the player

        # first let's create a new array that represents what the user would see
        visible_board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        for row in range(self.dim_size):
            for col in range(self.dim_size):
                if (row,col) in self.dug:
                    visible_board[row][col] = str(self.board[row][col])
                else:
                    visible_board[row][col] = ' '
        
        for cor in flag:
            visible_board[cor[0]][cor[1]] = '*'
        
        # put this together in a string
        string_rep = ''
        # get max column widths for printing
        widths = []
        for idx in range(self.dim_size):
            columns = map(lambda x: x[idx], visible_board)
            widths.append(
                len(
                    max(columns, key = len)
                )
            )

        # print the csv strings
        indices = [i for i in range(self.dim_size)]
        indices_row = '   '
        cells = []
        for idx, col in enumerate(indices):
            format = '%-' + str(widths[idx]) + "s"
            cells.append(format % (col))
        indices_row += '  '.join(cells)
        indices_row += '  \n'
        
        for i in range(len(visible_board)):
            row = visible_board[i]
            string_rep += f'{i} |'
            cells = []
            for idx, col in enumerate(row):
                format = '%-' + str(widths[idx]) + "s"
                cells.append(format % (col))
            string_rep += ' |'.join(cells)
            string_rep += ' |\n'

        str_len = int(len(string_rep) / self.dim_size)
        string_rep = indices_row + '-'*str_len + '\n' + string_rep + '-'*str_len

        return string_rep

    def visible(self):
        # this is a magic function where if you call print on this object,
        # it'll print out what this function returns!
        # return a string that shows the board to the player

        # first let's create a new array that represents what the user would see
        visible_board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        for row in range(self.dim_size):
            for col in range(self.dim_size):
                if (row,col) in self.dug:
                    visible_board[row][col] = self.board[row][col]
                else:
                    visible_board[row][col] = None
        return visible_board


class Game:
    def __init__(self,board):

        self.flags = set()
        self.dug = set()

        self.board_data = board
    
    def dig(self, row, col):
        # dig at that location!
        # return True if successful dig, False if bomb dug

        # a few scenarios:
        # hit a bomb -> game over
        # dig at location with neighboring bombs -> finish dig
        # dig at location with no neighboring bombs -> recursively dig neighbors!

        if (row, col) in self.flags:
            check = input("R U SURE? [Y/n]")
            if check == "n" or check == "N":
                return True
            self.flags.remove((row, col))

        # Initialize a stack for iterative approach
        stack = [(row, col)]
        
        while stack:
            current_row, current_col = stack.pop()
            self.dug.add((current_row, current_col))  # keep track that we dug here
            
            if self.board_data.board[current_row][current_col] == '*':
                # Hit a bomb, game over
                return False
            elif self.board_data.board[current_row][current_col] > 0:
                # Hit a cell with neighboring bombs, continue
                continue
            
            # self.board[current_row][current_col] == 0
            for r in range(max(0, current_row-1), min(self.board_data.dim_size-1, current_row+1)+1):
                for c in range(max(0, current_col-1), min(self.board_data.dim_size-1, current_col+1)+1):
                    if (r, c) in self.dug:
                        continue  # skip cells already dug
                    stack.append((r, c))

        # If our initial dig didn't hit a bomb, we *shouldn't* hit a bomb here
        return True

    def flag(self, row, col):
        self.flags.add((row,col))
        
    def game_data(self):
        return [['*' if (i, j) in self.flags else cell if (i, j) in self.dug else None for j, cell in enumerate(row)] for i, row in enumerate(self.board_data.board)]
    
    def won(self):
        return len(self.dug) == self.board_data.dim_size**2 - self.board_data.num_bombs

    @classmethod
    def new(cls, dim_size, num_bombs):
        return cls(Board(dim_size, num_bombs))




# play the game
def play(dim_size=10, num_bombs=10):
    # Step 1: create the board and plant the bombs
    board = Board(dim_size, num_bombs)

    # Step 2: show the user the board and ask for where they want to dig
    # Step 3a: if location is a bomb, show game over message
    # Step 3b: if location is not a bomb, dig recursively until each square is at least
    #          next to a bomb
    # Step 4: repeat steps 2 and 3a/b until there are no more places to dig -> VICTORY!
    safe = True 

    while len(board.dug) < board.dim_size ** 2 - num_bombs:
        print(board)
        # 0,0 or 0, 0 or 0,    0
        user_input = re.split(',(\\s)*', input("Where would you like to dig? Input as row,col: "))  # '0, 3'
        row, col = int(user_input[0]), int(user_input[-1])
        if row < 0 or row >= board.dim_size or col < 0 or col >= dim_size:
            print("Invalid location. Try again.")
            continue

        # if it's valid, we dig
        safe = board.dig(row, col)
        if not safe:
            # dug a bomb ahhhhhhh
            break # (game over rip)

    # 2 ways to end loop, lets check which one
    if safe:
        print("CONGRATULATIONS!!!! YOU ARE VICTORIOUS!")
    else:
        print("SORRY GAME OVER :(")
        # let's reveal the whole board!
        board.dug = [(r,c) for r in range(board.dim_size) for c in range(board.dim_size)]
        print(board)



def bot_play(dim_size=100, num_bombs=1000):
    # Step 1: create the board and plant the bombs
    board = Board(dim_size, num_bombs)
    
    # Step 2: show the user the board and ask for where they want to dig
    # Step 3a: if location is a bomb, show game over message
    # Step 3b: if location is not a bomb, dig recursively until each square is at least
    #          next to a bomb
    # Step 4: repeat steps 2 and 3a/b until there are no more places to dig -> VICTORY!
    safe = True 

    while len(board.dug) < board.dim_size ** 2 - num_bombs:
        print(board)
        print (num_bombs-len(flag))
        add_line_to_file(str(board), "C:\\Users\\zampr\\Desktop\\DATI.txt")
        # 0,0 or 0, 0 or 0,    0

        row, col = bot(board.visible(), num_bombs-len(flag))

        print(f'{row} - {col}')

        if row < 0 or row >= board.dim_size or col < 0 or col >= dim_size:
            print("Invalid location. Try again.")
            continue

        # if it's valid, we dig
        safe = board.dig(row, col)
        if not safe:
            # dug a bomb ahhhhhhh
            break # (game over rip)

    # 2 ways to end loop, lets check which one
    if safe:
        print("CONGRATULATIONS!!!! YOU ARE VICTORIOUS!")
    else:
        print("SORRY GAME OVER :(")
        # let's reveal the whole board!
        board.dug = [(r,c) for r in range(board.dim_size) for c in range(board.dim_size)]
        print(board)

def bot(visible_board, remaining_bombs, flags):
    
    rows = len(visible_board)
    colums = len(visible_board[0])
    
    for _ in range(100):
        for cor in flags:
            visible_board[cor[0]][cor[1]] = '*'

        for r in range(rows):
            for c in range(colums):
                if visible_board[r][c] == None or visible_board[r][c] == 0:
                    continue
                
                intorno_vuoto = intorno(visible_board,r,c,None)
                intorno_bombe = intorno(visible_board,r,c,'*')

                if visible_board[r][c] == len(intorno_bombe):
                    if len(intorno_vuoto)>0:
                        cor = list(intorno_vuoto)[0]
                        return cor[0],cor[1]

                if visible_board[r][c] == len(intorno_vuoto) + len(intorno_bombe):
                    flags = flags | intorno_vuoto
            
    user_input = re.split(',(\\s)*', input("Where would you like to dig? Input as row,col: "))  # '0, 3'
    r, c = int(user_input[0]), int(user_input[-1])
    return r,c

def bot_gui(game):

    visible_board = game.game_data()
    
    rows = len(visible_board)
    colums = len(visible_board[0])
    
    for _ in range(100):
        for cor in game.flags:
            visible_board[cor[0]][cor[1]] = '*'

        for r in range(rows):
            for c in range(colums):
                if visible_board[r][c] == None or visible_board[r][c] == 0:
                    continue
                
                intorno_vuoto = intorno(visible_board,r,c,None)
                intorno_bombe = intorno(visible_board,r,c,'*')

                if visible_board[r][c] == len(intorno_bombe):
                    if len(intorno_vuoto)>0:
                        cor = list(intorno_vuoto)[0]
                        return cor[0],cor[1]

                if visible_board[r][c] == len(intorno_vuoto) + len(intorno_bombe):
                    game.flags = game.flags | intorno_vuoto
            
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                posizione_mouse = pygame.mouse.get_pos()
                r, c = posizione_a_indici(posizione_mouse, altezza/dim)
                return r,c

def add_line_to_file(text, full_path):

    # Open the file in append mode or create the file if it doesn't exist
    with open(full_path, 'a+') as file:

        file.write('\n')

        # Add the line with the input text
        file.write(text)
    
    return
            



def intorno(board,row,col,number):

    rows = len(board)
    colums = len(board[0])

    count = set()
    for r in range(max(0, row-1), min(rows-1, row+1)+1):
        for c in range(max(0, col-1), min(colums-1, col+1)+1):
            if r == row and c == col:
                # our original location, don't check
                continue
            if board[r][c] == number:
                count.add((r,c))
    return count


def posizione_a_indici(posizione, dimensione):
    """Calcola gli indici del quadrato corrispondente alla posizione del mouse"""
    x, y = posizione
    riga = y // dimensione
    colonna = x // dimensione
    return riga, colonna


def disegna_griglia_con_numeri(schermo, griglia, dimensione_quadrato):
    """Disegna la griglia con i numeri/caratteri corrispondenti"""
    for riga in range(len(griglia)):
        for colonna in range(len(griglia[0])):
            x = colonna * dimensione_quadrato
            y = riga * dimensione_quadrato
            rettangolo = pygame.Rect(x, y, dimensione_quadrato, dimensione_quadrato)
            pygame.draw.rect(schermo, nero, rettangolo, 1)  # disegna il bordo del rettangolo

            # Aggiungi il numero/carattere al centro del quadrato
            font = pygame.font.Font(None, 36)  # Imposta il font e la dimensione del testo
            testo = font.render(str(griglia[riga][colonna] if griglia[riga][colonna] != None else " "), True, nero)  # Crea il testo
            testo_rettangolo = testo.get_rect(center=(x + dimensione_quadrato // 2, y + dimensione_quadrato // 2))
            schermo.blit(testo, testo_rettangolo)


def gui_play(game):
    pygame.init()

    # Dimensioni della finestra di gioco
    global larghezza
    global altezza

    # Colori
    global bianco
    global nero

    # Numero di quadrati per riga e per colonna
    numero_quadrati = dim
    dimensione_quadrato = larghezza // numero_quadrati

    # Creazione della finestra
    finestra = pygame.display.set_mode((larghezza, altezza))
    pygame.display.set_caption("MineSweeper")

    # Loop del gioco
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                posizione_mouse = pygame.mouse.get_pos()
                x, y = posizione_a_indici(posizione_mouse, dimensione_quadrato)

                # Rileva il tasto del mouse premuto
                if event.button == 1:  # Tasto sinistro del mouse
                    print("Tasto sinistro del mouse premuto a posizione:", posizione_mouse)
                    print(posizione_a_indici(posizione_mouse, dimensione_quadrato))
                    safe = game.dig(x, y)
                    if safe == False:
                        running = False
                        print("You lost!")
                    elif game.won():
                        running = False
                        print("You won!")
                elif event.button == 3:  # Tasto destro del mouse
                    print("Tasto destro del mouse premuto a posizione:", posizione_mouse)
                    game.flag(x, y)



        # Pulisci la finestra
        finestra.fill(bianco)

        # Disegna la griglia di quadrati
        disegna_griglia_con_numeri(finestra, game.game_data(),dimensione_quadrato)

        # Aggiornamento della finestra
        pygame.display.update()

    # Uscita dal programma
    pygame.quit()

def gui_bot(game):
    pygame.init()

    # Dimensioni della finestra di gioco
    global larghezza
    global altezza

    # Colori
    global bianco
    global nero

    # Numero di quadrati per riga e per colonna
    numero_quadrati = dim
    dimensione_quadrato = larghezza // numero_quadrati

    # Creazione della finestra
    finestra = pygame.display.set_mode((larghezza, altezza))
    pygame.display.set_caption("MineSweeper")

    # Loop del gioco
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                posizione_mouse = pygame.mouse.get_pos()
                x, y = bot_gui(game)

                # Rileva il tasto del mouse premuto
                if event.button == 3:  # Tasto sinistro del mouse
                    print("Tasto sinistro del mouse premuto a posizione:", posizione_mouse)
                    print(posizione_a_indici(posizione_mouse, dimensione_quadrato))
                    safe = game.dig(x, y)
                    if safe == False:
                        running = False
                        print("You lost!")



        # Pulisci la finestra
        finestra.fill(bianco)

        # Disegna la griglia di quadrati
        disegna_griglia_con_numeri(finestra, game.game_data(),dimensione_quadrato)

        # Aggiornamento della finestra
        pygame.display.update()

    # Uscita dal programma
    pygame.quit()


larghezza = 1000
altezza = 1000
dim = 10
bomb = 10

nero = (0, 0, 0)
bianco = (255, 255, 255)


if __name__ == '__main__': # good practice :)

    ##game = Game.new(dim,bomb)

    bot_play()

    ##gui_play(game)
    