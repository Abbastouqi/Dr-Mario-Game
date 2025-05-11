# from game_logic import Game
# from ui import display_field, display_level_status

# def main():
#     rows = int(input())
#     cols = int(input())

#     init_type = input().strip()
#     game = Game(rows, cols)

#     if init_type == "EMPTY":
#         pass
#     elif init_type == "CONTENTS":
#         field_data = [input() for _ in range(rows)]
#         game.load_field(field_data)

#     first_render = True  # <-- This prevents instant 'YOU WIN!' on first render

#     while True:
#         display_field(game)

#         if not first_render and game.is_level_cleared():
#             display_level_status("YOU WIN!")
#             break
#         first_render = False

#         print(f"Score: {game.score} | Combo: x{game.combo}")
#         command = input()
#         if command.strip().upper() == "Q":
#             break
#         game.process_command(command)

# if __name__ == '__main__':
#     main()



from game_logic import GameState
import shlex

def display_field(state: GameState):
    """Display the current state of the game field."""
    for r in range(state.get_rows()):
        row_display = '|'
        for c in range(state.get_columns()):
            row_display += state.get_cell_display(r, c)
        row_display += '|'
        print(row_display)
    print(' ' + '-' * (3 * state.get_columns()) + ' ')
    if not state.has_viruses():
        print('LEVEL CLEARED')

def main():
    """Main game loop."""
    # Read field dimensions
    rows = int(input())
    columns = int(input())
    
    # Read initial configuration
    config = input().strip()
    contents = None
    if config == 'CONTENTS':
        contents = [input().strip() for _ in range(rows)]
    
    # Initialize game state
    state = GameState(rows, columns, config, contents)
    
    # Main game loop
    while True:
        display_field(state)
        if state.game_over:
            print('GAME OVER')
            break
        
        command = input().strip()
        if command == 'Q':
            break
        elif command == '':
            if state.faller:
                if state.faller_landed:
                    state.freeze_faller()
                else:
                    state.faller_fall()
            state.apply_gravity()
        elif command.startswith('F'):
            parts = shlex.split(command)
            if len(parts) == 3 and parts[1] in ('R', 'B', 'Y') and parts[2] in ('R', 'B', 'Y'):
                state.create_faller(parts[1], parts[2])
        elif command == 'A':
            state.rotate_faller(True)
        elif command == 'B':
            state.rotate_faller(False)
        elif command == '<':
            state.move_faller_left()
        elif command == '>':
            state.move_faller_right()
        elif command.startswith('v'):
            parts = shlex.split(command)
            if len(parts) == 4 and parts[3] in ('r', 'y', 'b'):
                try:
                    row, col = int(parts[1]), int(parts[2])
                    if 0 <= row < state.get_rows() and 0 <= col < state.get_columns():
                        state.create_virus(row, col, parts[3])
                except ValueError:
                    pass

if __name__ == '__main__':
    main()