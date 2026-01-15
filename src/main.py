import time
import datetime
import os
from tetris_engine import TetrisGame
from ai_player import GeneticPlayer
import json

STATS_MODE = False # Stats mode makes it output only the final score, useful for statistics
GAMES_TO_RUN = 1

def print_board(game):
    # clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"Score: {game.score}")
    print("+" + "-" * (game.width * 2) + "+")
    
    for row in game.board:
        line = "|"
        for cell in row:
            # [] = blocks, . = empty space
            line += "[]" if cell else " ."
        line += "|"
        print(line)
        
    print("+" + "-" * (game.width * 2) + "+")

def main():
    # loading brain (from trainer.py)
    if os.path.exists("brains/best_brain.json"):
        print("loading AI brain from file...")
        with open("brains/best_brain.json", "r") as f:
            champion = json.load(f)
            weights = champion[1]
            
            print(f"loaded old champion:")
            print(f"loaded score: {champion[0]}")
            print(f"loaded weights: {champion[1]}")
    else:
        # manually inputted weights (super greedy)
        print("no brain file found, using manual weights.")
        weights = {
            "lines": 100.0,
            "height": -2.0,
            "holes": -10.0,
            "bumpiness": -1.0
        }
        
    player = GeneticPlayer(weights)
    
    # play the game(s)
    for i in range(GAMES_TO_RUN): 
        game = TetrisGame()
        # print("playing...")
        
        total_moves = 0
        start_time = datetime.datetime.now()
        
        # game loop
        while not game.game_over:
            # ask the AI for the best move, which returns (column, rotation)
            move = player.get_best_move(game)
            
            # if AI returns None, it means no moves are possible
            if not move:
                print("AI gave up (No moves possible)")
                break
                
            col, rot, swap_hold = move
            
            # stats
            total_moves += 1
            
            # executes moves
            reward = game.step(col, rot, swap_hold)
            
            # print board + time between frames (uncomment if you want to see it actually play)
            if(not STATS_MODE): 
                print_board(game)
                time.sleep(0.5)
            # if(swap_hold): 
            #     print("Swapping Hold")

        if(STATS_MODE):
            print(f"{game.score}") 
            # print_board(game) # for examining final board states
        else: 
            print(f"Final Score: {game.score}")
            print(f"Total Moves: {total_moves}")
            print(f"Time Elapsed: {datetime.datetime.now() - start_time}")
        
        

if __name__ == "__main__":
    main()