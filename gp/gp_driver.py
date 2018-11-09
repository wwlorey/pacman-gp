import controllers.game_state as game_state_class
import controllers.ghosts_controller as ghosts_cont_class
import controllers.pacman_controller as pacman_cont_class
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

        self.run_count = 1
        self.eval_count = 1
        self.local_best_score = -1

        self.log = log_class.Log(self.config, self.seed, overwrite=True)

        self.global_best_score = -1

        self.gpac_world = gpac_world_class.GPacWorld(self.config, initial_instance=True)

        self.pacman_cont = pacman_cont_class.PacmanController(self.config)
        self.ghosts_cont = ghosts_cont_class.GhostsController(self.config)

        self.game_state = game_state_class.GameState(self.gpac_world.pacman_coord, self.gpac_world.ghost_coords, self.gpac_world.pill_coords)


    def execute_turn(self):
        """Executes one game turn.

        First, all units are moved. Second, the game state is updated.
        """
        self.update_game_state()
        self.move_units()


    def begin_run(self):
        """Initializes run variables and writes a run header
        to the log file. 

        This should be called before each run.
        """
        self.eval_count = 1
        self.local_best_score = -1
        self.log.write_run_header(self.run_count)


    def end_run(self):
        """Increments the run count by one.
        
        This should be called after each run.
        """
        self.run_count += 1


    def begin_eval(self):
        """(Re)initializes the GPacWorld class member variable and adds walls to the
        game state.
        
        This should be called prior to each evaluation.
        """
        self.gpac_world = gpac_world_class.GPacWorld(self.config)
        self.game_state.update_walls(self.gpac_world.wall_coords)


    def end_eval(self):
        """Conditionally updates the log and world files and increments 
        the evaluation count.

        This should be called after each evaluation.
        """
        self.check_update_log_world_files()
        self.eval_count += 1


    def update_game_state(self):
        """Updates the state of the game *before* all characters have moved."""
        if len(self.gpac_world.fruit_coord):
            fruit_coord = self.gpac_world.fruit_coord

        else:
            fruit_coord = None

        self.game_state.update(self.gpac_world.pacman_coord, self.gpac_world.ghost_coords, self.gpac_world.pill_coords, fruit_coord)


    def move_units(self):
        """Moves all units in self.gpac_world based on the unit controller moves.
        
        Before units are moved, a fruit probabilistically spawns and the game state
        is updated.

        After units are moved, game variables are updated.
        """
        self.gpac_world.randomly_spawn_fruit()

        self.update_game_state()

        self.gpac_world.move_pacman(self.pacman_cont.get_move(self.game_state))

        for ghost_id in range(len(self.gpac_world.ghost_coords)):
            self.gpac_world.move_ghost(ghost_id, self.ghosts_cont.get_move(ghost_id, self.game_state))

        # Update time remaining
        self.gpac_world.time_remaining -= 1

        # Update pills
        if self.gpac_world.pacman_coord in self.gpac_world.pill_coords:
            self.gpac_world.pill_coords.remove(self.gpac_world.pacman_coord)
            self.gpac_world.num_pills_consumed += 1

        # Update fruit
        if self.gpac_world.pacman_coord in self.gpac_world.fruit_coord:
            self.gpac_world.fruit_coord.remove(self.gpac_world.pacman_coord)
            self.gpac_world.num_fruit_consumed += 1

        # Update score
        self.gpac_world.update_score()

        # Update the world state
        self.gpac_world.world_file.save_snapshot(self.gpac_world.pacman_coord,
            self.gpac_world.ghost_coords, self.gpac_world.fruit_coord, 
            self.gpac_world.time_remaining, self.gpac_world.score)


    def decide_termination(self):
        """Returns False if the program will terminate, True otherwise.

        The program will terminate if any of the following conditions are True:
            1. The number of evaluations specified in config has been reached.
        """
        if self.eval_count >= int(self.config.settings['num fitness evals']):
            # The number of desired evaluations has been reached
            return False

        return True


    def check_game_over(self):
        """Returns False if the game is over (allowing for a loop to terminate), 
        and True otherwise.

        The conditions for game over are seen in check_game_over() in the GPacWorld class.
        """
        if self.gpac_world.check_game_over():
            return False

        return True


    def check_update_log_world_files(self):
        """Writes a new log file entry iff a new local best score is found and writes
        transcript of this run to the world file iff it had the 
        global best score."""
        # Determine if a new local best score (fitness) has been found
        if self.gpac_world.score > self.local_best_score:
            self.local_best_score = self.gpac_world.score

            # Write log file row
            self.log.write_run_data(self.eval_count, self.local_best_score)

        # Determine if a new global best score has been found
        if self.gpac_world.score > self.global_best_score:
            self.global_best_score = self.gpac_world.score

            # Write to world file
            self.gpac_world.world_file.write_to_file()

