from tetris_engine import TetrisGame
import random

# Mutation stats
BASE_MUTATION_RATE = 0.1
BASE_MUTATION_STEP = 2.0

# Height penalty
HEIGHT_PENALTY_TOGGLE = True
HEIGHT_PENALTY_EXPONENT = 2.5
HEIGHT_PENALTY_BONUS = 36 # small reward for staying around 0-5 (more weighted towards 5)

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
        wells = self.calculate_wells(heights)
        lines = self.count_completed_lines(board)
        
        # extra penalties
        height_penalty = 0
        if HEIGHT_PENALTY_TOGGLE: 
            height_penalty = self._calculate_height_penalty(heights)
            
        
        # move score
        score = 0
        
        # multiply raw stats by weights and sum it
        score += agg_height * weights.get("height", 0)
        score += holes * weights.get("holes", 0)
        score += bumpiness * weights.get("bumpiness", 0)
        score += wells * weights.get("wells", 0)
        score += lines * weights.get("lines", 0)
        
        # score penalties
        score -= height_penalty
        
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
    
    def calculate_wells(self, heights): 
        total_wells = 0
        
        for i in range(len(heights)): 
            is_it_a_well = True
            
            # check left
            if i > 0: 
                if heights[i - 1] - heights[i] < 4: 
                    is_it_a_well = False
            
            # check right
            if i < len(heights) - 1: 
                if heights[i + 1] - heights[i] < 4: 
                    is_it_a_well = False

            if is_it_a_well: 
                total_wells += 1
        
        return total_wells
    
    def count_completed_lines(self, board): 
        return sum([1 for row in board if all(row)])
    
    def _get_col_height(self, board, x):
        # helper to find the height of a specific column x
        height = len(board)
        for y in range(height):
            if board[y][x] != 0:
                return height - y
        return 0
    
    def _calculate_height_penalty(self, heights): 
        total_penalty = 0
        exponent = HEIGHT_PENALTY_EXPONENT
        
        for height in heights: 
            if(height > 5): # don't reward stacking super high (> 5)
                total_penalty += ((height - 5) ** exponent)
            
        return total_penalty
            
                

# currently drop only, there's no tucking/sliding yet
class MoveScanner: 
    def get_all_possible_moves(self, game): 
        moves = []
        
        swapped_hold = False
        moves.extend(self._scan_board_using_piece(game, swapped_hold)) # scan using current piece
        
        swapped_hold = True
        moves.extend(self._scan_board_using_piece(game, swapped_hold)) # scan using held piece

        # returns a list of all possible moves (with current and held piece)
        return moves
    
    def _add_piece_to_board(self, board, piece, x, y): 
        # helper to put the piece onto the temp board
        for r, row in enumerate(piece): 
            for c, val in enumerate(row): 
                if val: 
                    board[y + r][x + c] = 1
                    
    def _scan_board_using_piece(self, game, swapped_hold): 
        piece_moves = []
        
        piece = game.current_piece
        if(swapped_hold): 
            piece = game.held_piece
            if(piece is None): 
                piece = game.get_piece_preview()[0]
        
        # loop through 4 possible rotations
        for rotation in range(4): 
            # rotates the base piece
            rotated_piece = game.rotate_piece(piece, rotation)
                
            # -3 to allow for pieces to fit into the left side columns (matrix rotation issues)
            for col in range(-3, game.width): 
                # fit at top of board? 
                if not game.is_valid_position(game.board, rotated_piece, col, 0):
                    continue
                
                # find where piece lands
                drop_y = game.get_drop_position(rotated_piece, col, rotation)
                
                # simulate move
                temp_board = [row[:] for row in game.board]
                self._add_piece_to_board(temp_board, rotated_piece, col, drop_y)
                
                # add move to possible moves
                piece_moves.append((temp_board, col, rotation, swapped_hold))
                
        return piece_moves
            

class GeneticPlayer: 
    def __init__(self, weights):
        self.weights = weights
        self.scanner = MoveScanner()
        self.evaluator = BoardEvaluator()
        
    def get_best_move(self, game):
        # use MoveScanner to get all options
        moves = self.scanner.get_all_possible_moves(game)
        
        best_score = -float('inf')
        best_move = None
        
        # use BoardEvaluator to score moves using self.weights
        for move in moves: 
            # get the board from the tuple
            board_state = move[0]
            
            # calculate score
            score = self.evaluator.get_score(board_state, self.weights)
            
            # track winning move
            if score > best_score: 
                best_score = score
                best_move = move
                
        if best_move is None: 
            return None
            
        # return the column, rotation, and swap_hold of the best move
        return (best_move[1], best_move[2], best_move[3])
    
    def get_genome(self): 
        return self.weights
    

# helper functions for generating, crossing over, and mutating weights
def generate_random_genome(): 
    return {
        "height": random.uniform(-50, 0),
        "holes": random.uniform(-50, 0), 
        "bumpiness": random.uniform(-50, 0),
        "wells": random.uniform(0, 50),
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

def mutate(weights, mutation_rate=BASE_MUTATION_RATE, mutation_step = BASE_MUTATION_STEP): 
    mutated_weights = weights.copy() 
    
    for key in mutated_weights: 
        if(random.random() < mutation_rate): 
            mutated_weights[key] += random.uniform(-mutation_step, mutation_step)
    
    return mutated_weights