import controllers.game_state as game_state_class
import controllers.ghosts_controller as ghosts_cont_class
import controllers.pacman_controller as pacman_cont_class
import gp.gpac_world_individual as gpac_world_individual_class
import gp.log as log_class
import random
import util.seed as seed_class
import world.gpac_world as gpac_world_class


class GPDriver:
    def __init__(self, config):
        """Initializes the GPDriver class.
        
        Where config is a Config object.
        """
        self.config = config

        self.seed = seed_class.Seed(self.config)

        self.population_size = int(self.config.settings['mu'])
        self.child_population_size = int(self.config.settings['lambda'])
        self.parent_population_size = int(self.config.settings['num parents'])

        self.run_count = 1
        self.eval_count = 1
        self.local_best_score = -1

        self.log = log_class.Log(self.config, self.seed, overwrite=True)

        self.global_best_score = -1

        self.population = []
        self.parents = []
        self.children = []


    def begin_run(self):
        """Initializes run variables and writes a run header
        to the log file. 

        This should be called before each run.
        """
        self.eval_count = 1
        self.local_best_score = -1
        self.log.write_run_header(self.run_count)

        # Initialize the population
        self.population = []
        for _ in range(self.population_size):
            world = gpac_world_class.GPacWorld(self.config)
            game_state = game_state_class.GameState(world.pacman_coords, world.ghost_coords, world.pill_coords, self.get_num_adj_walls(world, world.pacman_coords[0]))
            pacman_cont = pacman_cont_class.PacmanController(self.config)
            ghosts_cont = ghosts_cont_class.GhostsController(self.config)
            game_state.update_walls(world.wall_coords)

            self.population.append(gpac_world_individual_class.GPacWorldIndividual(world, game_state, pacman_cont, ghosts_cont))

            pacman_cont.visualize()


    def end_run(self):
        """Increments the run count by one.
        
        This should be called after each run.
        """
        self.run_count += 1


    def end_eval(self, individual):
        """Conditionally updates the log and world files and increments 
        the evaluation count.

        This should be called after each evaluation.
        """
        individual.fitness = individual.world.score
        self.check_update_log_world_files(individual)
        self.eval_count += 1
        print(self.eval_count)


    def evaluate(self, population):
        """Evaluates all population members given in population by running
        each world's game until completion. 
        """
        for individual in population:
            while self.check_game_over(individual):
                self.move_units(individual)

            self.end_eval(individual)


    def select_parents(self):
        """Chooses which parents from the population will breed.

        Depending on the parent selection configuration, one of the three following 
        methods is used to select parents:
            1. Fitness proportional selection
            2. Over-selection

        The resulting parents are stored in self.parents.
        """
        self.parents = []

        if self.config.settings.getboolean('use fitness proportional parent selection'):
            # Select parents for breeding using the fitness proportional "roulette wheel" method (with replacement)
            self.parents = random.choices(self.population, weights=[individual.fitness for individual in self.population], k=self.parent_population_size)
        
        else:
            # Default to over-selection parent selection
            pass        


    def recombine(self):
        """TODO: Breeds lambda (offspring pool size) children using sub-tree crossover 
        from the existing parent population. The resulting children are stored in 
        self.children.
        """

        def breed(parent_a, parent_b):
            """Performs sub-tree crossover on parent_a and parent_b returning the child tree."""

            def copy_subtree_recursive(node_a, node_b, count = 0):
                """Copies node_b and all of node_b's children into node_a."""
                if node_b.is_leaf():
                    node_a.children = []
                    return

                node_a.add_children([node.value for node in node_b.children])
                print(node_a)

                copy_subtree_recursive(node_a.left(), node_b.left(), count + 1)
                copy_subtree_recursive(node_a.right(), node_b.right(), count + 1)


            # Generate a list of each parent's state evaluator nodes
            node_list_a = parent_a.pacman_cont.state_evaluator.get_node_list()
            node_list_b = parent_b.pacman_cont.state_evaluator.get_node_list()

            # Choose a random node (crossover point) from each state evaluator node list
            crossover_node_a = node_list_a[random.randrange(0, len(node_list_a))]
            crossover_node_b = node_list_b[random.randrange(0, len(node_list_b))]
            insertion_node = tree.Node(crossover_node_a.value)


            crossover_node_a.value = crossover_node_b.value
            copy_subtree_recursive(crossover_node_a, crossover_node_b)

            world = gpac_world_class.GPacWorld(self.config)
            game_state = game_state_class.GameState(world.pacman_coords, world.ghost_coords, world.pill_coords, self.get_num_adj_walls(world, world.pacman_coords[0]))
            pacman_cont = parent_a.pacman_cont
            ghosts_cont = parent_a.ghosts_cont
            game_state.update_walls(world.wall_coords)


            child = gpac_world_individual_class.GPacWorldIndividual(world, game_state, pacman_cont, ghosts_cont)
            return child


        self.children = []

        for _ in range(self.child_population_size):
            # Select parents with replacement
            # Note: this implementation allows for parent_a and parent_b to be the same genotype
            parent_a = self.parents[random.randint(0, len(self.parents) - 1)]
            parent_b = self.parents[random.randint(0, len(self.parents) - 1)]

            # Produce a child
            self.children.append(breed(parent_a, parent_b))
        

    def mutate(self):
        """TODO: Probabilistically performs mutation on each child in the child population."""
        pass
        

    def select_for_survival(self):
        """TODO: Survivors are selected based on the following configurable methods:
            1. k-tournament selection without replacement
            2. Truncation

        Survivors are stored in self.population.
        """
        if self.config.settings.getboolean('comma survival strategy'):
            # Use the comma survival strategy
            selection_pool = self.children
        
        else:
            # Default to plus survival strategy
            selection_pool = self.population + self.children


        if self.config.settings.getboolean('use k tournament survival selection'):
            # Use k-tournament for survival selection without replacement
            pass
        
        else:
            # Default to truncation survival selection
            self.sort_individuals(selection_pool)
            self.population = selection_pool[:self.population_size]


    def update_game_state(self, individual):
        """Updates the state of the game *before* all characters have moved."""
        if len(individual.world.fruit_coord):
            fruit_coord = individual.world.fruit_coord

        else:
            fruit_coord = None

        individual.game_state.update(individual.world.pacman_coords, individual.world.ghost_coords, individual.world.pill_coords, self.get_num_adj_walls(individual.world, individual.world.pacman_coords[0]), fruit_coord)


    def move_units(self, individual):
        """Moves all units in individual.world based on the unit controller moves.
        
        Before units are moved, a fruit probabilistically spawns and the game state
        is updated.

        After units are moved, game variables are updated.
        """
        individual.world.randomly_spawn_fruit()

        self.update_game_state(individual)

        individual.world.move_pacman(individual.pacman_cont.get_move(individual.game_state))

        for ghost_id in range(len(individual.world.ghost_coords)):
            individual.world.move_ghost(ghost_id, individual.ghosts_cont.get_move(ghost_id, individual.game_state))

        # Update time remaining
        individual.world.time_remaining -= 1

        for pacman_coord in individual.world.pacman_coords:
            # Update pills
            if pacman_coord in individual.world.pill_coords:
                individual.world.pill_coords.remove(pacman_coord)
                individual.world.num_pills_consumed += 1

            # Update fruit
            if pacman_coord in individual.world.fruit_coord:
                individual.world.fruit_coord.remove(pacman_coord)
                individual.world.num_fruit_consumed += 1

        # Update score
        individual.world.update_score()

        # Update the world state
        individual.world.world_file.save_snapshot(individual.world.pacman_coords,
            individual.world.ghost_coords, individual.world.fruit_coord, 
            individual.world.time_remaining, individual.world.score)


    def decide_termination(self):
        """Returns False if the program will terminate, True otherwise.

        The program will terminate if any of the following conditions are True:
            1. The number of evaluations specified in config has been reached.
        """
        if self.eval_count >= int(self.config.settings['num fitness evals']):
            # The number of desired evaluations has been reached
            return False

        return True


    def check_game_over(self, individual):
        """Returns False if the game is over for the given individual (allowing for a loop to terminate), 
        and True otherwise.

        The conditions for game over are seen in check_game_over() in the GPacWorld class.
        """
        if individual.world.check_game_over():
            return False

        return True


    def check_update_log_world_files(self, individual):
        """Writes a new log file entry iff a new local best score is found and writes
        transcript of this run to the world file iff it had the 
        global best score.
        
        TODO: update this
        """
        # Determine if a new local best score (fitness) has been found
        if individual.world.score > self.local_best_score:
            self.local_best_score = individual.world.score

            # Write log file row
            self.log.write_run_data(self.eval_count, self.local_best_score)

        # Determine if a new global best score has been found
        if individual.world.score > self.global_best_score:
            self.global_best_score = individual.world.score

            # Write to world file
            individual.world.world_file.write_to_file()


    def get_num_adj_walls(self, world, coord):
        """Returns the number of walls adjacent to coord in the given world."""
        return len([c for c in world.get_adj_coords(coord) if c in world.wall_coords])


    def sort_individuals(self, individuals):
        individuals.sort(key=lambda x : x.fitness, reverse=True)
