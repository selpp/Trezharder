from spawner import Spawner
import random

class RandomSpawner(Spawner):
    def __init__(self):
        pass

    def spawn(self,spawn_number,map):
        spawns = []
        possible_spawns = []
        for x in range(len(map)):
            for y in range(len(map[x])):
                if map[x][y] == 0:
                    possible_spawns.append((x,y))
        if spawn_number == -1:
            spawn_number = len(possible_spawns)
        for i in range(spawn_number):
            spawn = possible_spawns.pop(random.randint(0,len(possible_spawns) - 1))
            spawns.append(spawn)

        return spawns