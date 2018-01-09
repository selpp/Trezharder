from engine.core.monobehaviour import MonoBehaviour
from engine.core.physics.collider import BoxCollider
from engine.core.maths.vector import Vector

class Goal(MonoBehaviour):
    def __init__(self):
        MonoBehaviour.__init__(self,1)

    def start(self):
        BoxCollider(self.transform,Vector(0,0),Vector(1,1),self.gameobject,True)
