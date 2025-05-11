
from typing import List, Tuple, Optional
import shlex

class GameState:
    """Represents the state of the Dr. Mario game."""
    
    def __init__(self, rows: int, columns: int, initial_config: str, contents: Optional[List[str]] = None):
        """
        Initialize the game field.
        
        Args:
            rows: Number of rows in the field (at least 4).
            columns: Number of columns in the field (at least 3).
            initial_config: 'EMPTY' or 'CONTENTS' to specify initial field state.
            contents: List of strings representing initial field contents if initial_config is 'CONTENTS'.
        """
        self.rows: int = rows
        self.columns: int = columns
        self.field: List[List[str]] = [[' ' for _ in range(columns)] for _ in range(rows)]
        self.faller: Optional[List[Tuple[int, int, str, bool]]] = None  # (row, col, color, is_left)
        self.faller_landed: bool = False
        self.game_over: bool = False
        
        if initial_config == 'CONTENTS' and contents:
            for r in range(rows):
                for c in range(columns):
                    self.field[r][c] = contents[r][c]
    
    def get_rows(self) -> int:
        """Return the number of rows in the field."""
        return self.rows
    
    def get_columns(self) -> int:
        """Return the number of columns in the field."""
        return self.columns
    
    def has_viruses(self) -> bool:
        """Check if the field contains any viruses."""
        return any(cell in ('r', 'y', 'b') for row in self.field for cell in row)
    
    def create_faller(self, color1: str, color2: str) -> bool:
        """
        Create a new faller at the top middle of the field.
        
        Args:
            color1: Color of the left segment (R, B, Y).
            color2: Color of the right segment (R, B, Y).
        
        Returns:
            bool: True if faller was created, False if it cannot be created.
        """
        if self.faller:
            return False
        mid = (self.columns // 2) - 1
        if self.field[1][mid] != ' ' or self.field[1][mid + 1] != ' ':
            self.game_over = True
            return False
        self.faller = [(1, mid, color1, True), (1, mid + 1, color2, False)]
        self.faller_landed = False
        return True
    
    def move_faller_left(self) -> bool:
        """Move the faller left if possible."""
        if not self.faller:
            return False
        row1, col1, color1, is_left1 = self.faller[0]
        row2, col2, color2, is_left2 = self.faller[1]
        
        if row1 == row2:  # Horizontal
            if col1 == 0 or self.field[row1][col1 - 1] != ' ':
                return False
            self.faller = [(row1, col1 - 1, color1, True), (row2, col2 - 1, color2, False)]
        else:  # Vertical
            if col1 == 0 or self.field[row1][col1 - 1] != ' ' or self.field[row2][col2 - 1] != ' ':
                return False
            self.faller = [(row1, col1 - 1, color1, True), (row2, col2 - 1, color2, False)]
        
        self.faller_landed = self.is_faller_landed()
        return True
    
    def move_faller_right(self) -> bool:
        """Move the faller right if possible."""
        if not self.faller:
            return False
        row1, col1, color1, is_left1 = self.faller[0]
        row2, col2, color2, is_left2 = self.faller[1]
        
        if row1 == row2:  # Horizontal
            if col2 == self.columns - 1 or self.field[row2][col2 + 1] != ' ':
                return False
            self.faller = [(row1, col1 + 1, color1, True), (row2, col2 + 1, color2, False)]
        else:  # Vertical
            if col1 == self.columns - 1 or self.field[row1][col1 + 1] != ' ' or self.field[row2][col2 + 1] != ' ':
                return False
            self.faller = [(row1, col1 + 1, color1, True), (row2, col2 + 1, color2, False)]
        
        self.faller_landed = self.is_faller_landed()
        return True
    
    def rotate_faller(self, clockwise: bool) -> bool:
        """
        Rotate the faller clockwise or counterclockwise.
        
        Args:
            clockwise: True for clockwise rotation (A command), False for counterclockwise (B command).
        
        Returns:
            bool: True if rotation was successful, False otherwise.
        """
        if not self.faller:
            return False
        row1, col1, color1, is_left1 = self.faller[0]
        row2, col2, color2, is_left2 = self.faller[1]
        
        if row1 == row2:  # Horizontal to vertical
            new_row = row1
            new_col = col1
            if new_row + 1 >= self.rows or self.field[new_row + 1][new_col] != ' ':
                if new_col > 0 and self.field[new_row][new_col - 1] == ' ' and (new_row + 1 >= self.rows or self.field[new_row + 1][new_col - 1] == ' '):
                    new_col -= 1  # Wall kick
                else:
                    return False
            self.faller = [(new_row, new_col, color1 if clockwise else color2, True),
                           (new_row + 1, new_col, color2 if clockwise else color1, False)]
        else:  # Vertical to horizontal
            new_row = row1
            new_col = col1
            if new_col + 1 >= self.columns or self.field[new_row][new_col + 1] != ' ':
                if new_col > 0 and self.field[new_row][new_col - 1] == ' ':
                    new_col -= 1  # Wall kick
                else:
                    return False
            self.faller = [(new_row, new_col, color2 if clockwise else color1, True),
                           (new_row, new_col + 1, color1 if clockwise else color2, False)]
        
        self.faller_landed = self.is_faller_landed()
        return True
    
    def is_faller_landed(self) -> bool:
        """Check if the faller has landed."""
        if not self.faller:
            return False
        row1, col1, _, _ = self.faller[0]
        row2, col2, _, _ = self.faller[1]
        
        if row1 == row2:  # Horizontal
            return (row1 == self.rows - 1 or
                    self.field[row1 + 1][col1] != ' ' or
                    self.field[row1 + 1][col2] != ' ')
        else:  # Vertical
            return row2 == self.rows - 1 or self.field[row2 + 1][col2] != ' '
    
    def faller_fall(self) -> bool:
        """Make the faller fall one cell if possible."""
        if not self.faller or self.faller_landed:
            return False
        row1, col1, color1, is_left1 = self.faller[0]
        row2, col2, color2, is_left2 = self.faller[1]
        
        if row1 == row2:  # Horizontal
            if row1 == self.rows - 1 or self.field[row1 + 1][col1] != ' ' or self.field[row1 + 1][col2] != ' ':
                self.faller_landed = True
                return False
            self.faller = [(row1 + 1, col1, color1, True), (row2 + 1, col2, color2, False)]
        else:  # Vertical
            if row2 == self.rows - 1 or self.field[row2 + 1][col2] != ' ':
                self.faller_landed = True
                return False
            self.faller = [(row1 + 1, col1, color1, True), (row2 + 1, col2, color2, False)]
        return True
    
    def freeze_faller(self):
        """Freeze the faller, converting it to regular capsule segments."""
        if not self.faller or not self.faller_landed:
            return
        row1, col1, color1, _ = self.faller[0]
        row2, col2, color2, _ = self.faller[1]
        self.field[row1][col1] = color1
        self.field[row2][col2] = color2
        self.faller = None
        self.faller_landed = False
        self.handle_matching()
    
    def create_virus(self, row: int, col: int, color: str) -> bool:
        """
        Create a virus at the specified position.
        
        Args:
            row: Row index (0-based).
            col: Column index (0-based).
            color: Virus color (r, y, b).
        
        Returns:
            bool: True if virus was created, False if cell is occupied.
        """
        if self.field[row][col] != ' ':
            return False
        self.field[row][col] = color
        return True
    
    def handle_matching(self):
        """Detect and remove matches, then apply gravity."""
        while True:
            matches = self.find_matches()
            if not matches:
                break
            for row, col in matches:
                self.field[row][col] = ' '
            self.apply_gravity()
    
    def find_matches(self) -> List[Tuple[int, int]]:
        """
        Find all cells involved in matches of 4 or more.
        
        Returns:
            List of (row, col) tuples for cells to be removed.
        """
        matches = set()
        
        # Check horizontal matches
        for r in range(self.rows):
            count = 1
            start = 0
            for c in range(1, self.columns):
                if self.field[r][c].lower() == self.field[r][c-1].lower() and self.field[r][c] != ' ':
                    count += 1
                else:
                    if count >= 4:
                        for i in range(start, c):
                            matches.add((r, i))
                    count = 1
                    start = c
            if count >= 4:
                for i in range(start, self.columns):
                    matches.add((r, i))
        
        # Check vertical matches
        for c in range(self.columns):
            count = 1
            start = 0
            for r in range(1, self.rows):
                if self.field[r][c].lower() == self.field[r-1][c].lower() and self.field[r][c] != ' ':
                    count += 1
                else:
                    if count >= 4:
                        for i in range(start, r):
                            matches.add((i, c))
                    count = 1
                    start = r
            if count >= 4:
                for i in range(start, self.rows):
                    matches.add((i, c))
        
        return list(matches)
    
    def apply_gravity(self):
        """Apply gravity to all capsules, moving them down as far as possible."""
        moved = True
        while moved:
            moved = False
            for r in range(self.rows - 2, -1, -1):
                for c in range(self.columns):
                    if self.field[r][c] in ('R', 'B', 'Y') and self.field[r + 1][c] == ' ':
                        self.field[r + 1][c] = self.field[r][c]
                        self.field[r][c] = ' '
                        moved = True
            self.handle_matching()
    
    def get_cell_display(self, row: int, col: int) -> str:
        """
        Get the 3-character display for a cell.
        
        Args:
            row: Row index.
            col: Column index.
        
        Returns:
            str: 3-character string representing the cell.
        """
        if self.faller:
            for r, c, color, is_left in self.faller:
                if r == row and c == col:
                    if self.faller_landed:
                        if r == self.faller[0][0] == self.faller[1][0]:  # Horizontal
                            return f"|{color}-" if is_left else f"-{color}|"
                        return f"|{color}|"
                    else:
                        if r == self.faller[0][0] == self.faller[1][0]:  # Horizontal
                            return f"[{color}-" if is_left else f"-{color}]"
                        return f"[{color}]"
        
        cell = self.field[row][col]
        if cell == ' ':
            return '   '
        if cell in ('r', 'y', 'b'):
            return f' {cell} '
        if cell in ('R', 'B', 'Y'):
            return f' {cell} '
        return '   '
