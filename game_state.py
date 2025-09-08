class GameState:
    def __init__(self):
        # Game state
        self.state = "intro"
        self.score = 0
        self.hits = 0
        self.misses = 0
        self.time_limit = 60_000  
        self.time_left = self.time_limit
        self.start_time = None
        self.sound_enabled = True
        self.occupied_holes = set() 

    def reset(self):
        self.score = 0
        self.hits = 0
        self.misses = 0
        self.time_left = self.time_limit
        self.start_time = None
        self.state = "intro"
        self.occupied_holes.clear() 