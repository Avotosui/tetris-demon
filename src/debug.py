from temp_tetris_engine import TetrisGame, Board, Piece, MoveScanner

game = TetrisGame()
board = Board()
scanner = MoveScanner() 

print(len(scanner.get_all_legal_moves(, game.spawn_piece())))


