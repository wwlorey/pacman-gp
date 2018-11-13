class GPacWorldIndividual:
    def __init__(self, world, game_state, pacman_cont, ghosts_cont, fitness=0):
        """Initializes the GPacWorldIndividual class."""
        self.world = world
        self.game_state = game_state
        self.pacman_cont = pacman_cont
        self.ghosts_cont = ghosts_cont
        self.fitness = fitness
