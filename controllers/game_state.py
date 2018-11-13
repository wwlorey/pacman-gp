class GameState:
    def __init__(self, pacman_coords, ghost_coords, pill_coords):
        """Initializes the GameState class."""
        self.update(pacman_coords, ghost_coords, pill_coords)

        self.wall_coords = None
        self.fruit_coord = None


    def update(self, pacman_coords, ghost_coords, pill_coords, fruit_coord=None):
        """Updates the GameState class."""
        self.pacman_coords = pacman_coords
        self.ghost_coords = ghost_coords
        self.pill_coords = pill_coords
        self.fruit_coord = fruit_coord


    def update_walls(self, wall_coords):
        """Updates the wall coordinates."""
        self.wall_coords = wall_coords
        