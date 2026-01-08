from tetris_engine import TetrisGame
import random

class BoardEvaluator: 
    def get_score(self, board, weights): 
        # calculates final score based on the weighted sum of heuristics
        # weights: a dictionary with weights like "height" or "lines"
        
        # Precalculate heights (assume board is standard 20 tall x 10 wide)
        width = len(board[0])
        heights = []
        for x in range(width):
            h = self._get_col_height(board, x)
            heights.append(h)
            
        # get raw stats
        agg_height = self.calculate_aggregate_height(board, heights)
        holes = self.calculate_holes(board, heights)
        bumpiness = self.calculate_bumpiness(heights)
        lines = self.count_completed_lines(board)
        
        # multiply by weights and sum it
        score = 0
        score += agg_height * weights.get("height", 0)
        score += holes      * weights.get("holes", 0)
        score += bumpiness  * weights.get("bumpiness", 0)
        score += lines      * weights.get("lines", 0)
        
        return score
    
    
    def calculate_aggregate_height(self, board, heights): 
        return sum(heights)
                
    
    def calculate_holes(self, board, heights): 
        holes = 0
        width = len(board[0])
        board_height = len(board)
        
        for x in range(width):
            col_height = heights[x]
            
            # empty column = skip
            if col_height == 0:
                continue
                
            # check from top down
            start_y = board_height - col_height
            for y in range(start_y, board_height):
                if board[y][x] == 0:
                    holes += 1
                    
        return holes
    
    def calculate_bumpiness(self, heights): 
        total_bumpiness = 0
        
        # sums the absolute difference between adjacent columns
        for i in range(len(heights) - 1): 
            total_bumpiness += abs(heights[i + 1] - heights[i])
            
        return total_bumpiness
    
    def count_completed_lines(self, board): 
        return sum([1 for row in board if all(row)])
    
    def _get_col_height(self, board, x):
        # helper to find the height of a specific column x
        height = len(board)
        for y in range(height):
            if board[y][x] != 0:
                return height - y
        return 0
                

# currently drop-only, there's no tucking/sliding yet
class MoveScanner: 
    def get_all_possible_moves(self, game, piece): 
        moves = []
        
        # loop through 4 possible rotations
        for rotation in range(4): 
            # rotates the base piece
            rotated_piece = game.rotate_piece(piece, rotation)
                
            # -3 to allow for pieces to fit into the side columns
            for col in range(-3, game.width): 
                # check validity, does it fit at top of board? 
                if not game.is_valid_position(game.board, rotated_piece, col, 0):
                    continue
                
                # find where piece lands
                drop_y = game.get_drop_position(rotated_piece, col, rotation)
                
                # simulate move
                temp_board = [row[:] for row in game.board]
                self._add_piece_to_board(temp_board, rotated_piece, col, drop_y)
                
                # add move to possible moves
                moves.append((temp_board, col, rotation))

        # returns a list of all possible moves
        return moves
    
    def _add_piece_to_board(self, board, piece, x, y): 
        # helper to put the piece onto the temp board
        for r, row in enumerate(piece): 
            for c, val in enumerate(row): 
                if val: 
                    board[y + r][x + c] = 1
            

class GeneticPlayer: 
    def __init__(self, weights):
        self.weights = weights
        self.scanner = MoveScanner()
        self.evaluator = BoardEvaluator()
        
    def get_best_move(self, game):
        # use MoveScanner to get all options
        moves = self.scanner.get_all_possible_moves(game, game.current_piece)
        
        best_score = -float('inf') 
        best_move = None
        
        # use BoardEvaluator to score moves using self.weights
        for move in moves: 
            # get the board from the tuple
            board_state = move[0]
            
            # calculate score
            score = self.evaluator.get_score(board_state, self.weights)
            
            # track winner
            if score > best_score: 
                best_score = score
                best_move = move
                
        if best_move is None: 
            return None
            
        # return the column and rotation of the best move
        return (best_move[1], best_move[2])
    
    def get_genome(self): 
        return self.weights
    

# helper functions for generating, crossing over, and mutating weights
def generate_random_genome(): 
    return {
        "height": random.uniform(-50, 0),
        "holes": random.uniform(-50, 0), 
        "bumpiness": random.uniform(-50, 0),
        "lines": random.uniform(0, 50)
    }

def crossover(parent1_weights, parent2_weights): 
    child_weights = {}
    
    for key in parent1_weights: 
        if(random.random() > 0.5): # 50% chance to inherit each parent's weights
            child_weights[key] = parent1_weights[key]
        else: 
            child_weights[key] = parent2_weights[key]
    return child_weights

def mutate(weights, mutation_rate=0.1, mutation_step = 2.0): 
    mutated_weights = weights.copy() 
    
    for key in mutated_weights: 
        if(random.random() < mutation_rate): 
            mutated_weights[key] += random.uniform(-mutation_step, mutation_step)
    
    return mutated_weights