import pygame
from game_logic import GameState

# Pygame initialization
pygame.init()
CELL_SIZE = 80  # Increased from 40 to 80 for larger interface
FPS = 60
FALL_INTERVAL = 0.5  # Time between faller drops (seconds)

# Colors
COLORS = {
    'R': (255, 0, 0), 'Y': (255, 255, 0), 'B': (0, 0, 255),
    'r': (255, 0, 0), 'y': (255, 255, 0), 'b': (0, 0, 255),
    ' ': (255, 255, 255), 'border': (0, 0, 0), 'text': (0, 0, 0)
}

class DrMarioGUI:
    """GUI for the Dr. Mario game using Pygame."""
    
    def __init__(self, rows: int, columns: int, config: str, contents: list = None):
        """
        Initialize the GUI and game state.
        
        Args:
            rows: Number of rows in the field.
            columns: Number of columns in the field.
            config: 'EMPTY' or 'CONTENTS' for initial field state.
            contents: List of strings for initial field contents if config is 'CONTENTS'.
        """
        self.state = GameState(rows, columns, config, contents)
        self.screen = pygame.display.set_mode((columns * CELL_SIZE, (rows + 2) * CELL_SIZE))
        pygame.display.set_caption("Dr. Mario")
        self.font = pygame.font.SysFont('arial', 48)  # Increased font size to match larger interface
        self.input_text = ""
        self.clock = pygame.time.Clock()
        self.last_fall_time = pygame.time.get_ticks() / 1000.0

    def draw_cell(self, row: int, col: int):
        """Draw a single cell based on its state."""
        x, y = col * CELL_SIZE, row * CELL_SIZE
        cell_display = self.state.get_cell_display(row, col)
        color = COLORS.get(cell_display[1], COLORS[' '])
        
        # Draw cell background
        pygame.draw.rect(self.screen, COLORS[' '], (x, y, CELL_SIZE, CELL_SIZE))
        
        # Draw content
        if cell_display != '   ':
            if cell_display[0] in ('[', '|'):  # Faller
                size = CELL_SIZE - 20  # Adjusted for larger cells
                offset = 10
                pygame.draw.rect(self.screen, color, (x + offset, y + offset, size, size))
                border_color = (0, 0, 0) if cell_display[0] == '[' else (100, 100, 100)
                pygame.draw.rect(self.screen, border_color, (x + offset, y + offset, size, size), 4)  # Thicker border
            elif cell_display[1] in ('r', 'y', 'b'):  # Virus
                size = CELL_SIZE - 20
                offset = 10
                pygame.draw.rect(self.screen, color, (x + offset, y + offset, size, size))
            else:  # Capsule
                size = CELL_SIZE - 20
                offset = 10
                pygame.draw.rect(self.screen, color, (x + offset, y + offset, size, size))
        
        # Draw connection lines for horizontal capsules/fallers
        if '-' in cell_display:
            line_y = y + CELL_SIZE // 2
            if cell_display[0] == '-':  # Right end
                pygame.draw.line(self.screen, COLORS['border'], (x, line_y), (x + CELL_SIZE // 2, line_y), 4)  # Thicker line
            elif cell_display[2] == '-':  # Left end
                pygame.draw.line(self.screen, COLORS['border'], (x + CELL_SIZE // 2, line_y), (x + CELL_SIZE, line_y), 4)

    def draw_field(self):
        """Draw the entire game field."""
        self.screen.fill((200, 200, 200))  # Background
        for r in range(self.state.get_rows()):
            for c in range(self.state.get_columns()):
                self.draw_cell(r, c)
        
        # Draw borders
        width, height = self.state.get_columns() * CELL_SIZE, self.state.get_rows() * CELL_SIZE
        pygame.draw.rect(self.screen, COLORS['border'], (0, 0, width, height), 4)  # Thicker border
        pygame.draw.line(self.screen, COLORS['border'], (0, height), (width, height), 4)
        
        # Draw status text
        if self.state.game_over:
            text = self.font.render("GAME OVER", True, COLORS['text'])
            self.screen.blit(text, (20, height + 20))
        elif not self.state.has_viruses():
            text = self.font.render("LEVEL CLEARED", True, COLORS['text'])
            self.screen.blit(text, (20, height + 20))
        
        # Draw input prompt
        prompt = self.font.render(f"Command: {self.input_text}", True, COLORS['text'])
        self.screen.blit(prompt, (20, height + 80))

    def handle_input(self):
        """Process keyboard input and update command buffer."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_RETURN:
                    self.process_command(self.input_text)
                    self.input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_a:
                    self.process_command("A")
                elif event.key == pygame.K_b:
                    self.process_command("B")
                elif event.key == pygame.K_LEFT:
                    print("Left Arrow pressed")
                    self.process_command("<")
                elif event.key == pygame.K_RIGHT:
                    print("Right Arrow pressed")
                    self.process_command(">")
                elif event.key == pygame.K_SPACE:
                    if self.input_text == "":
                        self.process_command("")
                    else:
                        self.input_text += " "
                elif event.unicode in ('F', 'V', 'R', 'Y', 'B', 'r', 'y', 'b', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
                    if event.unicode == 'F' and not self.input_text:
                        self.input_text = "F "
                    elif event.unicode == 'V' and not self.input_text:
                        self.input_text = "v "
                    else:
                        self.input_text += event.unicode
        return True

    def process_command(self, command: str):
        """Execute a game command."""
        print(f"Processing command: {command}")
        import shlex
        parts = shlex.split(command)
        print(f"Parsed parts: {parts}")
        if command == "Q":
            pygame.quit()
            return
        elif command == "":
            if self.state.faller:
                if self.state.faller_landed:
                    self.state.freeze_faller()
                else:
                    self.state.faller_fall()
            self.state.apply_gravity()
        elif command.startswith("F"):
            parts = shlex.split(command)
            if len(parts) == 3 and parts[1] in ('R', 'B', 'Y') and parts[2] in ('R', 'B', 'Y'):
                self.state.create_faller(parts[1], parts[2])
        elif command == "A":
            self.state.rotate_faller(True)
        elif command == "B":
            self.state.rotate_faller(False)
        elif command == "<":
            print("Moving faller left")
            self.state.move_faller_left()
        elif command == ">":
            print("Moving faller right")
            self.state.move_faller_right()
        elif command.startswith("v"):
            parts = shlex.split(command)
            if len(parts) == 4 and parts[3] in ('r', 'y', 'b'):
                try:
                    row, col = int(parts[1]), int(parts[2])
                    if 0 <= row < self.state.get_rows() and 0 <= col < self.state.get_columns():
                        self.state.create_virus(row, col, parts[3])
                except ValueError:
                    pass

    def run(self):
        """Main game loop for local execution."""
        running = True
        while running:
            current_time = pygame.time.get_ticks() / 1000.0
            if current_time - self.last_fall_time >= FALL_INTERVAL:
                self.process_command("")
                self.last_fall_time = current_time
            
            running = self.handle_input()
            self.draw_field()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

def main():
    """Entry point for the game."""
    rows = 8
    columns = 6
    config = "EMPTY"
    contents = None
    
    game = DrMarioGUI(rows, columns, config, contents)
    game.run()

if __name__ == "__main__":
    main()