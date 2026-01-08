import random

# For debugging
# random.seed(36)

# constants
MATRIX_HEIGHT = 20
MATRIX_WIDTH = 10

# based on the one-sided tetrominoes section of the Tetromino wikipedia page with correct starting orientations (flat)
SHAPES = {
    'I': [
        [0, 0, 0, 0], 
        [1, 1, 1, 1], 
        [0, 0, 0, 0], 
        [0, 0, 0, 0], 
    ],
    'O': [
        [1, 1],
        [1, 1]
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

class TetrisGame:
    def __init__(self, height=MATRIX_HEIGHT, width=MATRIX_WIDTH):
        self.height = height
        self.width = width
        self.score = 0
        self.game_over = False
        
        self.current_piece = None
        self.current_piece_key = None
        
        self.board = [[0] * width for _ in range(height)]
        self.bag = []
        
        self.spawn_piece()

    def rotate_piece(self, piece, rotations=1): 
        result = piece
        for _ in range(rotations % 4):
            result = [list(row) for row in zip(*result[::-1])]
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
    

    def get_drop_position(self, piece, column, rotation): 
        # finds the lowest a piece can drop to, given a piece and a x-coordinate
        drop_y = 0
        
        # keep moving until the piece hits something
        while(self.is_valid_position(self.board, piece, column, drop_y + 1)): 
            drop_y += 1
        
        return drop_y

    def step(self, column, rotation): 
        # AI players will call this to change the board to the next state
        # column = target column for piece ranging from 0-9
        # rotatoin = clockwise rotation index (0 = 0 deg, 1 = 90 deg, 2 = 180 deg, 3 = 270 deg)
        
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
        # refills the bag if it's empty
        if not self.bag: 
            self.bag = ['I', 'O', 'T', 'J', 'L', 'S', 'Z']
            random.shuffle(self.bag)
            
        # take a random piece out of the bag
        key = self.bag.pop()
        
        self.current_piece_key = key
        self.current_piece = SHAPES[key]
        
        # check middle spawn
        if not self.is_valid_position(self.board, self.current_piece, 3, 0): 
             self.game_over = True
        
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