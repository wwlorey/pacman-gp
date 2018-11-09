import time


class Seed:
    def __init__(self, config):
        """Initializes the Seed class.
        
        Where config is a Config object.
        """
        self.config = config

        if self.config.settings.getboolean('use external seed'):
            self.val = float(self.config.settings['seed'])
        
        else:
            self.val = time.time()
