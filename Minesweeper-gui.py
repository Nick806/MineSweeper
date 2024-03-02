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

"""
classi:
    Board_data
        dimensione righe
        domensione colonne
        numero di bombe
        array bidimensionale
        funzione per mettere i numeri
        bombe set()
    
    Visible
        dimensione righe
        domensione colonne
        numero di bombe
        numero di mosse
        scavate set()
        visible_board
        flags set()
        funz bombe rimanenti
    
    Game
        Board
        Visible
        won
        dig
    
    
"""

class Board_data():
    def __init__(self,rows,columns,n_bombs) -> None:
        self.rows = rows
        self.columns = columns
        self.n_bombs = n_bombs

        self.bombs = set()
        self.board = []

        self.init_board()

    def init_board(self):

        all_position = {(r,c) for c in range(self.columns) for r in range(self.rows)}

        while len(self.bombs)<self.n_bombs:
            self.bombs.add(random.choice(tuple(all_position - self.bombs)))

        self.board = [['*' if (r,c) in self.bombs else None for c in range(self.columns)] for r in range(self.rows)]

        self.assign_values_to_board()
    
    def assign_values_to_board(self):
        for r in range(self.rows):
            for c in range(self.columns):
                if self.board[r][c] == '*':
                    self.bombs.add((r,c))
                else:
                    self.board[r][c] = self.get_num_neighboring_bombs(r, c)

    def get_num_neighboring_bombs(self, row, col):
        # make sure to not go out of bounds!

        num_neighboring_bombs = 0
        for r in range(max(0, row-1), min(self.rows-1, row+1)+1):
            for c in range(max(0, col-1), min(self.columns-1, col+1)+1):
                if self.board[r][c] == '*':
                    num_neighboring_bombs += 1

        return num_neighboring_bombs
    
    def __str__(self) -> str:
        string = ""
        for r in self.board:
            for c in r:
                string += str(c)
                string += " "
            string += "\n"
        return string



"""Visible
        dimensione righe
        domensione colonne
        numero di bombe
        numero di mosse
        scavate set()
        visible_board
        flags set()
        funz bombe rimanenti"""

class Visible():
    def __init__(self,rows,columns,n_bombs) -> None:
        self.rows = rows
        self.columns = columns
        self.n_bombs = n_bombs

        self.n_moves = 0
        self.dug = set()
        self.flags = set()
        self.safe = set()
        self.board = []
    
    @property
    def remaining_bombs(self) -> int:
        return self.n_bombs - len(self.flags)
    
    def flag(self, x) -> None:
        if type(x) == tuple:
            self.flags.add(x)
        if type(x) == set:
            self.flags = self.flags | x
    
    def unflag(self, x) -> None:
        if type(x) == tuple:
            self.flags.discard(x)
        if type(x) == set:
            self.flags = self.flags - x

class Game():
    def __init__(self, rows, columns, n_bombs) -> None:
        self.rows = rows
        self.columns = columns
        self.n_bombs = n_bombs

        self.board_data = Board_data(rows, columns, n_bombs)
        self.visible = Visible(rows, columns, n_bombs)
        self.update_visible()
    
    @property
    def won(self):
        return len(self.visible.dug) == self.rows*self.columns - self.board_data.n_bombs
    
    def dig(self, row, col):

        # Initialize a stack for iterative approach
        stack = [(row, col)]
        
        while stack:
            current_row, current_col = stack.pop()
            self.visible.dug.add((current_row, current_col))  # keep track that we dug here
            
            if self.board_data.board[current_row][current_col] == '*':
                # Hit a bomb, game over
                return False
            elif self.board_data.board[current_row][current_col] > 0:
                # Hit a cell with neighboring bombs, continue
                continue
            
            # self.board[current_row][current_col] == 0
            for r in range(max(0, current_row-1), min(self.rows-1, current_row+1)+1):
                for c in range(max(0, current_col-1), min(self.columns-1, current_col+1)+1):
                    if (r, c) in self.visible.dug:
                        continue  # skip cells already dug
                    stack.append((r, c))

        # If our initial dig didn't hit a bomb, we *shouldn't* hit a bomb here

        self.update_visible()
        return True

    def update_visible(self):
        self.visible.dug
        self.visible.board = [[self.board_data.board[r][c] if (r,c) in self.visible.dug else "*" if (r,c) in self.visible.flags  else " " for c in range(self.columns)] for r in range(self.rows)]
    
    def dig_safe(self):
        for cor in self.visible.safe:
            self.dig(cor[0], cor[1])
        self.visible.safe = set()
    
    def help(self):
        for r in range(self.rows):
            for c in range(self.columns):
                if self.board_data.board[r][c] != 0:
                    continue
                if (r,c) in self.visible.dug:
                    continue
                self.dig(r,c)
                return

def posizione_a_indici(posizione):
    """Calcola gli indici del quadrato corrispondente alla posizione del mouse"""
    global window_data

    x, y = posizione
    riga = y // (window_data['height']/game_data['rows'])
    colonna = x // (window_data['width']/game_data['columns'])
    return int(riga), int(colonna)


def disegna_griglia_con_numeri(griglia):
    """Disegna la griglia con i numeri/caratteri corrispondenti"""
    global window
    rows = len(griglia)
    columns = len(griglia[0])

    cell_width = window_data['width'] / columns
    cell_height = window_data['height'] / rows

    for riga in range(rows):
        for colonna in range(columns):
            x = colonna * cell_width
            y = riga * cell_height
            rettangolo_bordo = pygame.Rect(x, y, cell_width,cell_height)
            rettangolo_riempimento = pygame.Rect(x+2, y+2, cell_width,cell_height-2)
            #pygame.draw.rect(window, colors['black'], rettangolo, 1)  # disegna il bordo del rettangolo
            # Disegna il bordo del rettangolo
            pygame.draw.rect(window, colors['black'], rettangolo_bordo)

            # Riempimento del rettangolo con un colore diverso (es. verde)
            pygame.draw.rect(window, colors['black'] if (riga, colonna) in game.visible.safe else number_colors[griglia[riga][colonna]], rettangolo_riempimento)

            # Aggiungi il numero/carattere al centro del quadrato
            font = pygame.font.Font(None, 36)  # Imposta il font e la dimensione del testo
            testo = font.render(str(griglia[riga][colonna] if griglia[riga][colonna] != None else " "), True, colors['black'])  # Crea il testo
            testo_rettangolo = testo.get_rect(center=(x + cell_width // 2, y + cell_height // 2))
            window.blit(testo, testo_rettangolo)


def Bot(visible):
    def get_intorno(t):
        x = t[0]
        y = t[1]
        s = set()
        for a in range(max(0,x-1), min(x+2,visible.rows)):
            for b in range(max(0,y-1), min(y+2,visible.columns)):
                s.add((a,b))
        return s
    
    def get_intorno_vuote(t):
        return get_intorno(t)-visible.dug

    def conta_intorno_vuote(t):
        return len(get_intorno_vuote(t))

    def get_intorno_bombe(t):
        return get_intorno(t) & visible.flags

    def conta_intorno_bombe(t):
        return len(get_intorno_bombe(t))

    def flag_all_obvious():
        for cor in visible.dug:
            assert (type(visible.board[cor[0]][cor[1]]) == int, "Cosa sea sta roba?")
            if visible.board[cor[0]][cor[1]] == 0:
                continue
            if visible.board[cor[0]][cor[1]] == conta_intorno_vuote(cor):
                visible.flag(get_intorno_vuote(cor))
                n_flagged = 1

    def dig_all_obvious():
        b = 0
        for cor in visible.dug:
            assert (type(visible.board[cor[0]][cor[1]]) == int, "Cosa sea sta roba?")
            if visible.board[cor[0]][cor[1]] == 0:
                continue
            if visible.board[cor[0]][cor[1]] == conta_intorno_bombe(cor):
                if conta_intorno_vuote(cor) != 0:
                    visible.safe = visible.safe | (get_intorno_vuote(cor) - get_intorno_bombe(cor))
                    n_digged = 1
    
    def bruteforce():
        board = [[None for c in range(visible.columns)] for r in range(visible.rows)]
        for cor in visible.dug:
            if visible.board[cor[0]][cor[1]] == 0:
                continue
            if visible.board[cor[0]][cor[1]] == conta_intorno_bombe(cor)-1:
                clear = get_intorno(cor)-visible.dug-visible.flags
                if len(clear) == 2:
                    num = cor[0]*visible.rows+cor[1]
                    for c in clear:
                        board[c[0]][c[1]] = num
        pass

    
    n_flagged = 0
    n_digged = 0

    flag_all_obvious()
    if n_flagged == 0: dig_all_obvious()
    if n_digged == 0: bruteforce()


colors = {
    'black'  : (  0,   0,   0),
    'blue'   : (  0,   0, 255),
    'green'  : (  0, 128,   0),
    'lime'   : (  0, 255,   0),
    'maroon' : (128,   0,   0),
    'navy'   : (  0,   0, 128),
    'olive'  : (128, 128,   0),
    'purple' : (128,   0, 128),
    'red'    : (255,   0,   0),
    'teal'   : (  0, 128, 128),
    'white'  : (255, 255, 255),
    'yellow' : (255, 255,   0),
}

number_colors = {
    " "  : (255, 255, 255),  # Cella Vuota: Bianco
    1    : (0, 0, 255),      # Numero 1: Blu
    2    : (0, 128, 0),      # Numero 2: Verde Scuro
    3    : (0, 255, 0),      # Numero 3: Verde Chiaro
    4    : (128, 0, 0),      # Numero 4: Rosso Scuro
    5    : (0, 0, 128),      # Numero 5: Blu Scuro
    6    : (128, 128, 0),    # Numero 6: Giallo Scuro
    7    : (128, 0, 128),    # Numero 7: Viola Scuro
    8    : (255, 0, 0),      # Numero 8: Rosso Chiaro
    0    : (192, 192, 192),  # Cella Vuota (Nessun vicino): Grigio
    "*"  : (255, 0, 0)       # Bomba: Rosso Chiaro

}

symbols = {
    'mine'  : "*",
    'flag'  : "F",
}

window_data = {'width' :1000,
          'height':1000}

game_data = {'rows' : 50,
             'columns': 50,
             'bombs': 400}




if __name__ == '__main__':
    pygame.init()

    window = pygame.display.set_mode((window_data['width'], window_data['height']))
    pygame.display.set_caption("MineSweeper")

    game = Game(game_data['rows'],game_data['columns'],game_data['bombs'])

    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                posizione_mouse = pygame.mouse.get_pos()
                x, y = posizione_a_indici(posizione_mouse)

                # Rileva il tasto del mouse premuto
                if event.button == 1:  # Tasto sinistro del mouse
                    print("Tasto sinistro del mouse premuto a posizione:", posizione_mouse)
                    print(posizione_a_indici(posizione_mouse))
                    safe = game.dig(x, y)
                    if safe == False:
                        running = False
                        print("You lost!")
                    elif game.won:
                        running = False
                        print("You won!")
                elif event.button == 3:  # Tasto destro del mouse
                    print("Tasto destro del mouse premuto a posizione:", posizione_mouse)
                    if (x,y) in game.visible.flags:
                        game.visible.unflag((x,y))
                    else:
                        game.visible.flag((x, y))
                    game.update_visible()

            # Rileva l'evento di premere un tasto
            elif event.type == pygame.KEYDOWN:
                posizione_mouse = pygame.mouse.get_pos()
                x, y = posizione_a_indici(posizione_mouse)
                # Se il tasto premuto è la freccia sinistra, cambia il colore del rettangolo
                if event.key == pygame.K_d or event.key == pygame.K_c:
                    print("Tasto sinistro del mouse premuto a posizione:", posizione_mouse)
                    print(posizione_a_indici(posizione_mouse))
                    safe = game.dig(x, y)
                    if safe == False:
                        running = False
                        print("You lost!")
                    elif game.won:
                        running = False
                        print("You won!")
                if event.key == pygame.K_f or event.key == pygame.K_x:
                    print("Tasto destro del mouse premuto a posizione:", posizione_mouse)
                    if (x,y) in game.visible.flags:
                        game.visible.unflag((x,y))
                    else:
                        game.visible.flag((x, y))
                    game.update_visible()
                if event.key == pygame.K_b:
                    Bot(game.visible)
                    game.dig_safe()
                    game.update_visible()
                if event.key == pygame.K_h:
                    game.help()
                    game.update_visible()    

        window.fill(colors['white'])
        disegna_griglia_con_numeri(game.visible.board)

        pygame.display.update()

    pygame.quit()

