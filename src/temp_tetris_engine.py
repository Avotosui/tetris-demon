from settings import MATRIX_HEIGHT, MATRIX_WIDTH, EXTRA_BOARD_HEIGHT, EXTRA_BOARD_WIDTH, PIECE_PREVIEW_AMOUNT, SHAPES, SRS_TABLE
import random
from collections import deque


class TetrisGame:
    def __init__(self):
        self.score = 0
        self.game_over = False
        
        self.current_piece = None
        self.held_piece = None
        
        self.board = Board()
        
        self.bag = []
        
    def spawn_piece(self):
        # refills the bag if it has less than 7 pieces
        if len(self.bag) < 7: 
            new_bag = ['I', 'O', 'T', 'J', 'L', 'S', 'Z']
            random.shuffle(new_bag)
            self.bag.extend(new_bag)
            
        # take a random piece out of the bag
        current_piece_key = self.bag.pop(0)
        
        # (x, y) for top-left corner of normal 3x3 matrices
        x = 3
        y = 0
        
        if(current_piece_key == 'I'): # unique spawn position cuz bigger matrix
            x = 2
            y = -2
            
        rotation = 0
        
        self.current_piece = Piece(x, y, rotation, current_piece_key)
        
        
        
class Piece: 
    # anchored in top left corner (x, y)
    def __init__(self, x, y, rotation, piece_key): 
        self.x = x
        self.y = y
        self.rotation = rotation
        self.piece_key = piece_key
        
    def get_current_position(self): 
        return (self.x, self.y)
    
    def get_current_shape(self): # does NOT return offsets, MUST do offsets later for rotations (for I and O pieces)
        result = SHAPES[self.piece_key]
        
        # matrix clockwise rotation code found online
        for i in range(self.rotation % 4): 
            result = [list(row) for row in zip(*result[::-1])]
            
        return result
    
    def print(self): 
        print((self.x, self.y, self.rotation, self.piece_key))
    
    

class Board: 
    def __init__(self, height=MATRIX_HEIGHT, width=MATRIX_WIDTH): 
        self.height = height
        self.width = width
        self.board = [[0] * width for _ in range(height)]
        
    def lock_piece(self, piece): 
        actual_piece = piece.get_current_shape()
        for r, row in enumerate(actual_piece): 
            for c, val in enumerate(row): 
                if val:
                    self.board[piece.y + r][piece.x + c] = 1
                    
    def clear_lines(self): 
        # clears all rows of only 1s
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        
        lines_cleared = self.height - len(new_board)
        for i in range(lines_cleared): 
            new_board.insert(0, [0] * self.width)
            
        self.board = new_board
        
        return lines_cleared



class MoveScanner: 
    def get_all_legal_moves(self, board, piece): 
        moves = []
        
        pk = piece.piece_key
        
        # BFS setup
        queue = deque()
        visited = set()
        
        queue.append((piece.x, piece.y, piece.rotation))
        visited.add((piece.x, piece.y, piece.rotation))
        
        while(queue): 
            cur_x, cur_y, cur_r = queue.popleft() 
            
            directions = [
                [-1, 0, 0], # left
                [1, 0, 0], # right
                [0, 1, 0] # down
            ]
            
            for dx, dy, dr in directions: 
                new_x, new_y, new_r = cur_x + dx, cur_y + dy, cur_r + dr
                
                if((new_x, new_y, new_r) not in visited): 
                    if(self.is_valid_position(board, new_x, new_y, new_r, pk)): 
                        visited.add((new_x, new_y, new_r))
                        queue.append((new_x, new_y, new_r))
                    elif(dx == 0 and dy == 1): 
                        moves.append(Piece(cur_x, cur_y, cur_r, pk)) # final move found (cuz it can't move down no more :skull:)
            
            rot_directions = [-1, 1]
            
            for dr in rot_directions: 
                new_r = (cur_r + dr) % 4
                
                kicks = SRS_TABLE[pk][cur_r][new_r]
                
                for kick in kicks: 
                    dx, dy = kick[0], kick[1]
                    new_x, new_y = cur_x + dx, cur_y + dy
                    
                    
                    if(self.is_valid_position(board, new_x, new_y, new_r, pk)): 
                        if((new_x, new_y, new_r) not in visited): 
                            visited.add((new_x, new_y, new_r))
                            queue.append((new_x, new_y, new_r))
                        break # possible rotation found OR already visited the possible kick -> end kick testing
    
        return moves
    
    
    def is_valid_position(self, board, start_x, start_y, start_rot, piece_key): 
        # checks if a piece fits at (target_x, target_y) coordinates
        # returns False if it hits the wall, hits the floor, or intersects with another block
        piece = Piece(start_x, start_y, start_rot, piece_key)
        
        actual_piece = piece.get_current_shape()
        
        for y, row in enumerate(actual_piece): 
            for x, cell in enumerate(row): 
                if cell: 
                    board_x = piece.x + x
                    board_y = piece.y + y

                    # check board boundaries
                    if board_x < 0 or board_x >= board.width:
                        return False
                    if board_y >= board.height:
                        return False

                    # check overlap with other blocks
                    if board_y >= 0:
                        if board.board[board_y][board_x] == 1:
                            return False
        return True

def test(): 
    board = Board()
    
    scanner = MoveScanner()
    
    moves = scanner.get_all_legal_moves(board, Piece(3, 0, 0, 'T'))
    
    print(len(moves))

if(__name__ == "__main__"): 
    test()