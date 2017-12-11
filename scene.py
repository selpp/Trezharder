# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from game_engine import GameEngineTools

class SceneManager(object):
    _current_scene = None
    _SceneType = None
        
    @staticmethod    
    def load(SceneType):
        if SceneManager._current_scene is not None:
            SceneManager._current_scene.on_destroy()
        SceneManager._current_scene = SceneType()
        SceneManager._SceneType = SceneType
        
        
    @staticmethod
    def restart():
        SceneManager._current_scene.on_destroy()
        SceneManager._current_scene = SceneManager._SceneType()

class Scene(object):
    __metaclass__ = ABCMeta
    
    def __init__(self):
        self.gameobjects = self.load()
        for gameobject in self.gameobjects:
            GameEngineTools.instantiate(gameobject)
        
    def on_destroy(self):
        for gameobject in self.gameobjects:
            if gameobject.is_alive:
                GameEngineTools.DestroyObject(gameobject)

    @abstractmethod
    def load(self):
        pass
        