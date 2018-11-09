#!/usr/bin/env python3

import gp.gp_driver as gp_driver_class
import util.args as args_class
import util.config as config_class

if __name__ == '__main__':

    # Process command line arguments
    args = args_class.Arguments(1, ['config/default.cfg'])
    config_file = args.get_args()[0]


    # Setup configuration
    config = config_class.Config(config_file)


    # Initialize the GP driver and its run variables
    gp_driver = gp_driver_class.GPDriver(config)


    # Run the GP
    while gp_driver.run_count <= int(config.settings['num experiment runs']):
        gp_driver.begin_run()

        while gp_driver.decide_termination():
            gp_driver.begin_eval()

            while gp_driver.check_game_over():
                gp_driver.execute_turn()

            gp_driver.end_eval()

        gp_driver.end_run()

