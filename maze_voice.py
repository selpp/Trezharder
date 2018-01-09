from monobehaviour import MonoBehaviour

class MazeVoice(MonoBehaviour):
    def __init__(self,notify_time = 5.0):
        MonoBehaviour.__init__(self)
        self.notify_time = notify_time
        self.listeners = []
    
    def start(self):
        self.timer = 0.0
    
    def add_listener(self,new_listener):
        self.listeners.append(new_listener)
    
    def notify_dispatch_weapon(self):
        remove_list = []
        for listener in self.listeners:
            listener.on_notify('dispatch')
            if isinstance(listener,MonoBehaviour) and not listener.gameobject.is_alive:
                remove_list.append(listener)
        for remove_listener in remove_list:
            self.listeners.remove(remove_listener)
    
    def update(self,dt):
        self.timer += dt
        if(self.timer > self.notify_time):
            self.notify_dispatch_weapon()
            self.timer = 0.0
        