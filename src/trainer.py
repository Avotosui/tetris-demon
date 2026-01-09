from tetris_engine import TetrisGame
from ai_player import GeneticPlayer, generate_random_genome, crossover, mutate
import json
import random
import os
import datetime


# training hyperparameters
POPULATION_SIZE = 30
GENERATIONS = 15

MOVES_LIMIT = 500
MOVES_LIMIT_SHIFTING_TOGGLE = True
MOVES_LIMIT_SHIFT_STEP = 500

SURVIVAL_RATE = 0.2
MUTATION_RATE = 0.1
MUTATION_STEP = 2.0

# game playing helper function
def playGame(weights): 
    tetris_game = TetrisGame()
    player = GeneticPlayer(weights)
    
    moves = 0
    while not tetris_game.game_over and moves < MOVES_LIMIT: 
        # get best move based on the player
        current_move = player.get_best_move(tetris_game)
        
        if not current_move: 
            break # AI gave up
        
        # make the move
        tetris_game.step(current_move[0], current_move[1], current_move[2])
        
        moves += 1
    
    return (tetris_game.score, moves)
    

def main(): 
    global MOVES_LIMIT
    
    start_time = datetime.datetime.now() 
    
    print("generating population...")
    population = [generate_random_genome() for _ in range(POPULATION_SIZE)]
    
    # best player stats
    best_player_weights = None
    best_player_moves = -1
    best_player_score = -1
    
    for generation in range(GENERATIONS): 
        print(f"<------Generation {generation + 1}------>")
        
        max_moves_hit = False
        
        population_results = []
        print("Training Started: ")
        for i, genome in enumerate(population): 
            player_results = playGame(genome)
            
            player_score = player_results[0]
            player_moves = player_results[1]
            
            if(player_moves >= MOVES_LIMIT and MOVES_LIMIT_SHIFTING_TOGGLE and not max_moves_hit): 
                # print("A player hit the moves limit! Increasing moves limit next generation...")
                max_moves_hit = True
            
            population_results.append((player_score, genome, player_moves))
            
            # show training progress
            print(".", end = "", flush = True)
        
        print()
        
        # sort scores by highest to lowest
        population_results.sort(key = lambda x: x[0], reverse = True)
        
        # output data for best
        print(f"Generation Best Score: {population_results[0][0]}")
        print(f"Weights: {population_results[0][1]}")
        print(f"Moves: {population_results[0][2]}")
        
        # output scores for everything
        just_scores = [round(x[0], 2) for x in population_results]
        print(f"All Population Scores: {just_scores}")
        
        # see if there's a new best player
        if population_results[0][0] > best_player_score: 
            print(f"NEW TRAINING SESSION BEST PLAYER!!!!!!")
            best_player_score = population_results[0][0]
            best_player_weights = population_results[0][1]
            best_player_moves = population_results[0][2]
            
        # max moves hit by a player -> extra moves being added (if toggled on)
        if(max_moves_hit and MOVES_LIMIT_SHIFTING_TOGGLE): 
            print(f"MAX MOVES HIT! Increasing the moves limit by {MOVES_LIMIT_SHIFT_STEP}")
            MOVES_LIMIT += MOVES_LIMIT_SHIFT_STEP
        
        # death and survivors
        cutoff = int(SURVIVAL_RATE * POPULATION_SIZE)
        survivors = [genome[1] for genome in population_results[:cutoff]]
        
        # build the next generation of players
        next_generation = survivors[:] # start with survivors
        
        # breeding
        while len(next_generation) < len(population): 
            # choose two random parents from the list of survivors
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            
            # make and mutate the child
            child = mutate(crossover(parent1, parent2), MUTATION_RATE, MUTATION_STEP)
            
            next_generation.append(child)
        
        # replace the population with the next generation
        population = next_generation[:]
    
    print(f"Training Finished.")
    
    # fitness calculation (probably useless lmao I was just playing around)
    best_player_fitness = best_player_score * (1 + best_player_score/best_player_moves)
    
    # saving the best player
    if os.path.exists("best_brain.json"):
        print("Loading past AI brain from file...")
        with open("best_brain.json", "r") as r:
            old_champion = json.load(r)
            if(old_champion[0] < best_player_score): 
                print(">>>>>>NEW ALL TIME BEST PLAYER!!!!!!<<<<<<")
                with open('best_brain.json', 'w') as w: 
                    json.dump((best_player_score, best_player_weights), w)
                print("Saved to best_brain.json")
            else: 
                print("The older player was better...")
                print("Nothing saved to best_brain.json")
    else:
        print("No AI brain loaded before...")
        print("Adding new AI brain")
        with open('best_brain.json', 'w') as w: 
            json.dump((best_player_score, best_player_weights), w)
        print("Saved to best_brain.json")
        
    print(f"Training Time Elapsed: {datetime.datetime.now() - start_time}")
    
        

if __name__ == "__main__":
    main()