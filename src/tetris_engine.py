import random
from collections import deque

# For debugging
# random.seed(36)

# constants
MATRIX_HEIGHT = 20
MATRIX_WIDTH = 10

PIECE_PREVIEW_AMOUNT = 3

# Guideline SRS Shapes
SHAPES = {
    'I': [
        [0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0], 
        [0, 1, 1, 1, 1], 
        [0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 0]
    ],
    'O': [
        [0, 1, 1],
        [0, 1, 1], 
        [0, 0, 0]
    ],
    'T': [
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0]
    ],
    'J': [
        [1, 0, 0], 
        [1, 1, 1], 
        [0, 0, 0]
    ],
    'L': [
        [0, 0, 1], 
        [1, 1, 1], 
        [0, 0, 0]
    ],
    'S': [
        [0, 1, 1], 
        [1, 1, 0], 
        [0, 0, 0]
    ],
    'Z': [
        [1, 1, 0], 
        [0, 1, 1], 
        [0, 0, 0]
    ]
}

# Tetris Guideline SRS Table (calculated from offsets)
# SRS[piece_key][original_rotation][final_rotation]
# 0 = base rotation, 1 = 90 degrees clockwise, 2 = 180 degrees clockwise, 3 = 270 degrees clockwise
# 0 = 0, 1 = R, 2 = 2, 3 = L (tetris.wiki/Super_Rotation_System)
SRS = {
    'I': [
        [None, [(1,0), (-1,0), (2,0), (-1,1), (2,-2)], None, [(0,1), (-1,1), (2,1), (-1,-1), (2,2)]], 
        [[(-1,0), (1,0), (-2,0), (1,-1), (-2,2)], None, [(0,1), (-1,1), (2,1), (-1,-1), (2,2)], None], 
        [None, [(0,-1), (1,-1), (-2,-1), (1,1), (-2,-2)], None, [(-1,0), (1,0), (-2,0), (1,-1), (-2,2)]],  
        [[(0,-1), (1,-1), (-2,-1), (1,1), (-2,-2)], None, [(1,0), (-1,0), (2,0), (-1,1), (2,-2)], None]
    ],
    'O': [
        [None, [(0,-1)], None, [(1,0)]],
        [[(0,1)], None, [(1,0)], None],
        [None, [(-1,0)], None, [(0,1)]],
        [[(-1,0)], None, [(0,-1)], None],
    ], 
    'T': [
        [None, [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], None, [(0,0), (1,0), (1,-1), (0,2), (1,2)]], 
        [[(0,0), (1,0), (1,1), (0,-2), (1,-2)], None, [(0,0), (1,0), (1,1), (0,-2), (1,-2)], None], 
        [None, [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], None, [(0,0), (1,0), (1,-1), (0,2), (1,2)]], 
        [[(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], None, [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], None]
    ], 
    'J': [
        [None, [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], None, [(0,0), (1,0), (1,-1), (0,2), (1,2)]], 
        [[(0,0), (1,0), (1,1), (0,-2), (1,-2)], None, [(0,0), (1,0), (1,1), (0,-2), (1,-2)], None], 
        [None, [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], None, [(0,0), (1,0), (1,-1), (0,2), (1,2)]], 
        [[(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], None, [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], None]
    ], 
    'L': [
        [None, [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], None, [(0,0), (1,0), (1,-1), (0,2), (1,2)]], 
        [[(0,0), (1,0), (1,1), (0,-2), (1,-2)], None, [(0,0), (1,0), (1,1), (0,-2), (1,-2)], None], 
        [None, [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], None, [(0,0), (1,0), (1,-1), (0,2), (1,2)]], 
        [[(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], None, [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], None]
    ], 
    'S': [
        [None, [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], None, [(0,0), (1,0), (1,-1), (0,2), (1,2)]], 
        [[(0,0), (1,0), (1,1), (0,-2), (1,-2)], None, [(0,0), (1,0), (1,1), (0,-2), (1,-2)], None], 
        [None, [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], None, [(0,0), (1,0), (1,-1), (0,2), (1,2)]], 
        [[(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], None, [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], None]
    ], 
    'Z': [
        [None, [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], None, [(0,0), (1,0), (1,-1), (0,2), (1,2)]], 
        [[(0,0), (1,0), (1,1), (0,-2), (1,-2)], None, [(0,0), (1,0), (1,1), (0,-2), (1,-2)], None], 
        [None, [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], None, [(0,0), (1,0), (1,-1), (0,2), (1,2)]], 
        [[(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], None, [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], None]
    ]
}

class TetrisGame:
    def __init__(self, height=MATRIX_HEIGHT, width=MATRIX_WIDTH):
        self.height = height
        self.width = width
        self.score = 0
        self.game_over = False
        
        self.current_piece = None
        self.current_piece_key = None
        
        self.held_piece = None
        self.held_piece_key = None
        
        self.board = [[0] * width for _ in range(height)]
        self.bag = []
        
        self.spawn_piece()

    def rotate_piece(self, piece, rotations=1): 
        # actual rotation
        result = piece
        for _ in range(rotations % 4):
            result = [list(row) for row in zip(*result[::-1])]
            # kick calculation (only actually does something for I and O pieces)
            # PLACEHOLDER
        
        # CHANGE TO INCLUDE THE KICK OFFSET
        return result
    
    def is_valid_position(self, board, piece, target_x, target_y):
        # checks if a piece fits at (target_x, target_y) coordinates
        # returns False if it hits the wall, hits the floor, or intersects with another block
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:  
                    board_x = target_x + x
                    board_y = target_y + y

                    # check board boundaries
                    if board_x < 0 or board_x >= self.width:
                        return False
                    if board_y >= self.height:
                        return False

                    # check overlap with other blocks
                    if board_y >= 0:
                        if board[board_y][board_x] == 1:
                            return False
        return True
    
    def find_kick(self, board, piece_key, original_rotation, final_rotation, x, y): 
        kicks = SRS[piece_key][original_rotation][final_rotation]
        
        for kick in kicks: 
            result = None
            for _ in range(rotations % 4):
                result = [list(row) for row in zip(*result[::-1])]
    

    def get_drop_position(self, piece, column, rotation): 
        # finds the lowest a piece can drop to, given a piece and a x-coordinate
        drop_y = 0
        
        # keep moving until the piece hits something
        while(self.is_valid_position(self.board, piece, column, drop_y + 1)): 
            drop_y += 1
        
        return drop_y

    def step(self, column, rotation, swap_hold): 
        # AI players will call this to change the board to the next state
        # column = target column for piece ranging from 0-9
        # rotation = clockwise rotation index (0 = 0 deg, 1 = 90 deg, 2 = 180 deg, 3 = 270 deg)
        # swap_hold = whether to swap to the held piece
        
        if(swap_hold): 
            self.hold_piece()
        
        # creates specific rotated piece
        original_shape = SHAPES[self.current_piece_key] 
        piece = self.rotate_piece(original_shape, rotation)
        
        # check if column is valid
        # if move is invalid, kill game + reward nothing
        if not self.is_valid_position(self.board, piece, column, 0):
             self.game_over = True
             return 0 # reward 0
             
        # calculate drop
        final_y = self.get_drop_position(piece, column, rotation)
        
        # lock piece onto board
        self.lock_piece(piece, column, final_y)
        
        # clear lines and get score
        lines_cleared = self.clear_lines()
        if(lines_cleared == 1): 
            self.score += 40
        elif(lines_cleared == 2): 
            self.score += 100
        elif(lines_cleared == 3): 
            self.score += 300
        elif(lines_cleared == 4): 
            self.score += 1200
            
        # 6. Spawn next piece
        self.spawn_piece()
        
        return self.score
    
    def lock_piece(self, piece, x, y): 
        # iterate over the piece and write 1s into self.board
        for r, row in enumerate(piece): 
            for c, val in enumerate(row): 
                if val:
                    self.board[y + r][x + c] = 1
                    
    def spawn_piece(self):
        # refills the bag if it has less than 7 pieces
        if len(self.bag) < 7: 
            new_bag = ['I', 'O', 'T', 'J', 'L', 'S', 'Z']
            random.shuffle(new_bag)
            self.bag.extend(new_bag)
            
        # take a random piece out of the bag
        key = self.bag.pop(0)
            
        self.current_piece_key = key
        self.current_piece = SHAPES[key]
        
        # check middle spawn
        if not self.is_valid_position(self.board, self.current_piece, 3, 0): 
             self.game_over = True
             
    def get_piece_preview(self): 
        return self.bag[:PIECE_PREVIEW_AMOUNT]
    
    def hold_piece(self): 
        # make placeholder for current piece
        temp_piece = self.current_piece
        temp_piece_key = self.current_piece_key
        
        # hasn't held a piece in this game yet, need to take out the next piece
        if(self.held_piece is None): 
            self.held_piece_key = self.bag.pop(0)
            self.held_piece = SHAPES[self.held_piece_key]
        
        # swap
        self.current_piece = self.held_piece
        self.current_piece_key = self.held_piece_key
        self.held_piece = temp_piece
        self.held_piece_key = temp_piece_key
        
        
    def clear_lines(self): 
        # removes completed lines and adds new empty ones on top
        # returns number of lines cleared
        
        # filter out full rows
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        
        # calculate how many rows were cleared and add that many to the top
        lines_cleared = self.height - len(new_board)
        for _ in range(lines_cleared):
            new_board.insert(0, [0] * self.width)
            
        # update normal board
        self.board = new_board
        
        # return score (currently 1 line = 1 score)
        return lines_cleared

class Board: 
    def __init__(self, height=MATRIX_HEIGHT, width=MATRIX_WIDTH): 
        self.height = height
        self.width = width
        self.board = [[0] * width for _ in range(height)]
        
    def clear_lines(self): 
        # removes completed lines and adds new empty ones on top
        # returns number of lines cleared
        
        # filter out full rows
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        
        # calculate how many rows were cleared and add that many to the top
        lines_cleared = self.height - len(new_board)
        for _ in range(lines_cleared):
            new_board.insert(0, [0] * self.width)
            
        # update normal board
        self.board = new_board
        
        # return score (currently 1 line = 1 score)
        return lines_cleared
        
class Piece: 
    # anchored in top left corner (x, y)
    def __init__(self, x, y, rotation, piece_key): 
        self.x = x
        self.y = y
        self.rotation = rotation
        self.piece_key = piece_key
    
    

class MoveScanner: 
    def find_all_legal_moves(game): 
        moves = []
        
        queue = deque()
        visited = [[False] * (game.width + 3) for _ in range(game.height)][4]
        
        
        # current piece, x, y, current rotation
        # queue.append((game.current_piece, skib, 0, 0))
        while(queue): 
            current_piece_position = queue.pop()
            # L, R, CW, CCW, drop 1
            # if drop cannot happen, then add to list of final moves