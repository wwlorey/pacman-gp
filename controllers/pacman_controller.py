import controllers.base_controller as base_controller_class
import controllers.direction as d
import controllers.nodes as nodes_classes
import controllers.tree as tree_class
import copy
import random


# Assign new node class names
terminals = nodes_classes.TerminalNodes
functions = nodes_classes.FunctionNodes


# Constant declarations
POSSIBLE_MOVES = [d.Direction.NONE, d.Direction.UP, d.Direction.DOWN, 
    d.Direction.LEFT, d.Direction.RIGHT]

NUM_POSSIBLE_CHILDREN = 2


class PacmanController(base_controller_class.BaseController):
    def __init__(self, config):
        """Initializes the PacmanController class."""
        self.config = config

        super(base_controller_class.BaseController, self).__init__()

        self.max_fp_constant = float(self.config.settings['max fp constant'])

        self.init_state_evaluator()


    def init_state_evaluator(self):
        """Initializes this controller's state evaluator tree."""
        target_height_met = False

        def init_state_evaluator_recursive(parent_node, current_depth=2):
            nonlocal target_height_met

            if current_depth == target_height:
                # End this branch
                target_height_met = True
                children = [self.get_rand_terminal_node() for _ in range(NUM_POSSIBLE_CHILDREN)]
                parent_node.add_children(children)
                return
            
            if target_height_met and current_depth < target_height and random.random() < float(self.config.settings['premature end prob']):
                # Prematurely end this branch
                children = [self.get_rand_terminal_node() for _ in range(NUM_POSSIBLE_CHILDREN)]
                parent_node.add_children(children)
                return

            # Continue constructing the tree
            children = [self.get_rand_function_node() for _ in range(NUM_POSSIBLE_CHILDREN)]
            parent_node.add_children(children)

            for child in parent_node.children:
                init_state_evaluator_recursive(child, current_depth + 1)


        target_height = random.randint(2, int(self.config.settings['max tree generation height']))
        self.state_evaluator = tree_class.Tree(self.config, self.get_rand_function_node())

        init_state_evaluator_recursive(self.state_evaluator.root)


    def get_rand_terminal_node(self):
        """Returns a random terminal node."""
        terminal_node = random.choices([node for node in terminals])[0]

        if terminal_node == terminals.FP_CONSTANT:
            # Return a floating point constant
            return random.uniform(0, self.max_fp_constant)

        return terminal_node


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
            pacman_coords = game_state.pacman_coords

        else:
            pacman_coords = [pacman_coord]

        return random.random()

    def visualize(self):
        """Prints a function representing the state evaluator."""

        def get_symbol(node):
            if node.value == terminals.PACMAN_GHOST_DIST:
                return 'ghost distance'

            if node.value == terminals.PACMAN_PILL_DIST:
                return 'pill distance'

            if node.value == terminals.PACMAN_FRUIT_DIST:
                return 'fruit distance'

            if node.value == terminals.NUM_ADJ_WALLS:
                return 'num adj walls'
                
            if node.value == functions.ADD:
                return '+'
                
            if node.value == functions.SUBTRACT:
                return '-'
                
            if node.value == functions.MULTIPLY:
                return '*'
                
            if node.value == functions.DIVIDE:
                return '/'
                
            if node.value == functions.RANDOM_FLOAT:
                return 'rand'

            return str(node.value)


        def visualize_recursive(node):
            if node.is_leaf():
                return get_symbol(node)

            return '( ' + visualize_recursive(node.left()) + ' ' + get_symbol(node) + ' ' + visualize_recursive(node.right()) + ' )'
        

        print(visualize_recursive(self.state_evaluator.root))
