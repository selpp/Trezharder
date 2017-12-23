from monobehaviour import MonoBehaviour
from scene import SceneManager

class RestartTimeOut(MonoBehaviour):
    def __init__(self,limit_time):
        MonoBehaviour.__init__(self)
        self.limit_time = limit_time
        self.time = 0.0
        
    def start(self):
        pass
        
    def fixed_update(self,fdt):
        self.time += fdt
        if self.time > self.limit_time:
            SceneManager.restart()