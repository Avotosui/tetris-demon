# Genetic Algorithm Tetris AI (Suibot☄️☄️☄️☄️☄️☄️)

This is a headless Tetris engine with an AI player that uses a genetic algorithm to tune its heuristic weights. It’s mainly a personal project for learning more about game AI and genetic algorithms.

## Project Features

- Headless Tetris Engine  
  A non-graphical Tetris simulator that runs faster and makes it easier to test ideas without worrying about rendering.

- Heuristic-Based AI  
  The AI decides where to place pieces using board features like height, bumpiness, holes, wells, and lines cleared. Each feature has a weight that affects how good a move looks.

- Genetic Algorithm  
  A genetic algorithm is used to automatically adjust those heuristic weights based on how well the AI performs, instead of tuning them by hand. 

- Placement Control  
  The AI picks a rotation and x-position, instead of using movement keys, and the engine places the piece there. 

## Future plans

- Add SRS support  
  Implement the Super Rotation System so rotations behave more like modern Tetris (and the AI will hopefully be able to do the T-Spins and such ).

- Translate placements into real inputs  
  Convert the AI’s placement decisions into actual keyboard inputs like left, right, rotate, and drop.

- Play on external Tetris clients  
  Use basic computer vision so the AI can read the screen and play games outside of the built-in engine.

## Brains

The various brains are my models based on different training/feature additions. 
- Brain V1 was trained with very basic Tetris, where the only inputs where the current piece, the board and the four basic heuristics
- Brain V2 has an added height penalty on the AI
- Brain V3 was trained with an updated Tetris engine where it is now able to hold a piece and preview up to three pieces (only processes the current piece and the held piece because my laptop isn't powerful enough to do very deep look-aheads)
- Brain V4 was worse than Brain V3; I tried implementing a piecewise function that rewarded lower heights up to 5 and disliked upper heights exponentially (wasn't great)
- Brain V5 has a new wells heuristic and reverted back to the old height penalty but now doesn't penalize lower heights (<= 5)
- Brain V6 was trained overnight with a cap on how many moves each player had (took about 7.5 hours), performs worse than previous models (seemingly because it liked having more than 1 well)

## Getting Started

**Requirements:** Python 3.x

Run `main.py` to see the current AI play in the headless engine. 
Run `trainer.py` if you wish to train your own genetic AI player (will override best_brain.json if it's better). 

## Notes

This project is mostly for my personal experimentation and learning. The code is still evolving, and a lot of things can definitely be improved.

## Contact

Maintainer: @Avotosui  
Email: avotosui@gmail.com