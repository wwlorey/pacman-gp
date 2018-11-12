import controllers.base_controller as base_controller_class
import controllers.direction as d
import controllers.nodes as nodes_classes
import controllers.tree as tree_class
import copy
import random


# Assign new node class names
terminals = nodes_classes.TerminalNodes
functions = nodes_classes.FunctionNodes


POSSIBLE_MOVES = [d.Direction.NONE, d.Direction.UP, d.Direction.DOWN, 
    d.Direction.LEFT, d.Direction.RIGHT]


class PacmanController(base_controller_class.BaseController):
    def __init__(self, config):
        """Initializes the PacmanController class."""
        self.config = config

        super(base_controller_class.BaseController, self).__init__()

        self.max_fp_constant = float(self.config.settings['max fp constant'])

        self.init_state_evaluator()


    def init_state_evaluator(self):
        """Initializes this controller's state evaluator tree."""
        # TODO: For now, this only creates a tree w/ function root and two children
        self.state_evaluator = tree_class.Tree(self.config, self.get_rand_function_node())
        self.state_evaluator.root.add_children([self.get_rand_terminal_node(), self.get_rand_terminal_node()])
        self.state_evaluator.visualize()


    def get_rand_terminal_node(self):
        """Returns a random terminal node."""
        terminal_node = random.choices([node for node in terminals])[0]

        if terminal_node == terminals.FP_CONSTANT:
            # Return a floating point constant
            return random.uniform(0, self.max_fp_constant)


    def get_rand_function_node(self):
        """Returns a random function node."""
        return random.choices([node for node in functions])[0]


    def get_move(self, game_state):
        """Checks all possible moves against the state evaluator and 
        determines which move is optimal, returning that move.

        This is performed for each pacman presented as part of the game state.
        """

        def move_pacman(pacman_coord, direction):
            """Alters pacman's new coordinate to indicate movement in direction.
            
            Returns True if the new position is valid, False otherwise.
            """
            if direction == d.Direction.NONE:
                # No action needed
                return True

            # Adjust new_coord depending on pacman's desired direction
            if direction == d.Direction.UP:
                pacman_coord.y += 1

            elif direction == d.Direction.DOWN:
                pacman_coord.y -= 1

            elif direction == d.Direction.LEFT:
                pacman_coord.x -= 1

            elif direction == d.Direction.RIGHT:
                pacman_coord.x += 1
            
            if self.check_valid_location(pacman_coord, game_state):
                return True

            return False


        best_eval_directions = []

        for pacman_coord in game_state.pacman_coords:
            best_eval_result = 0
            best_eval_direction = d.Direction.NONE

            for direction in POSSIBLE_MOVES:
                tmp_pacman_coord = copy.deepcopy(pacman_coord)

                if move_pacman(tmp_pacman_coord, direction):
                    eval_result = self.evaluate_state(game_state, tmp_pacman_coord)

                    if eval_result > best_eval_result:
                        best_eval_result = eval_result
                        best_eval_direction = direction
            
            best_eval_directions.append(best_eval_direction)

        return best_eval_directions
         

    def evaluate_state(self, game_state, pacman_coord=None):
        """Given a current (or potential) game state, a rating
        is provided from the state evaluator.

        Optional parameter pacman_coord can check a differing pacman
        coordinate against the state evaluator.
        """
        if not pacman_coord:
            pacman_coord = game_state.pacman_coord

        return random.random()

