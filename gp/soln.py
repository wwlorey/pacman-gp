import world.coordinate as coord_class


class Solution:
    def __init__(self, config):
        """Initializes the Solution class.

        Where config is a Config object.
        """
        self.config = config

    
    def write_to_file(self, individual):
        """Writes the given solution (PacmanController object) to the solution file."""
        file = open(self.config.settings['soln file path'], 'w')

        file.write('###################################\n# State Evaluator Tree (list format)\n###################################\n')
        file.write(str([n.value for n in individual.pacman_cont.state_evaluator]))
        file.write('\n\n')

        file.write('###################################\n# State Evaluator Equation\n###################################\n')
        file.write(individual.pacman_cont.visualize(print_output=False))
        file.write('\n')

        file.close()
