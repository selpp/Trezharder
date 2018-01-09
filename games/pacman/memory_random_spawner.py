from games.pacman.random_spawner import RandomSpawner

class MemoryRandomSpawner(RandomSpawner):
    def __init__(self):
        self.all_spawn()

    def spawn(self,map):
        RandomSpawner.spawn(self,map)
