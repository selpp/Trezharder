from player import Player
from copy import copy
from game_engine import GameEngineTools
from weapon import Weapon

class Brawler(Player):
    def __init__(self,command,color,ennemy_name):
        Player.__init__(self,command,color,ennemy_name)
        self.basic_power = 10
        self.life = 10
        self.weapons = []
        self.shoot_timer = 1.1
        self.attack_freq = 1.0
        
    def buff(self,power):
        self.power += power
        
    def update(self,dt):
        Player.update(self,dt)
        self.shoot_timer += dt
        
    def try_kill(self):
        if self.shoot_timer < self.attack_freq:
            return
        if len(self.weapons) == 0:
            return
        weapon_got_used = False
        current_power = self.compute_power()
        for ennemy in self.ennemies:
            if ennemy is None or ennemy is self.gameobject or not ennemy.is_alive:
                continue
            if (ennemy.transform.get_position() - self.transform.get_position()).magnitude() < 50.0:
                brawler = ennemy.get_mono(Brawler)
                brawler.damage(current_power)
                if brawler.rip:
                    self.murderer = True
                weapon_got_used = True
        if weapon_got_used:
            self.damage_all_weapons
            self.shoot_timer = 0.0
    
    def damage(self,power):
        if self.life <= 0:
            return
        self.life -= power
        if self.life < 1:
            self.die()
            
    def got_weapon(self,new_weapon):
        self.weapon.append(new_weapon)
        
    def give_weapons(self):
        tmp = copy(self.weapons)
        self.weapons = []
        return tmp
    
    def compute_power(self):
        power = self.basic_power
        for weapon in self.weapons:
            power += weapon.get_power()
        return power
        
    def damage_all_weapons(self):
        for weapon in self.weapons:
            weapon.damage()
            
    def on_collision(self,collider):
        if collider.parent_transform.tag == 'weapon':
            weapon = collider.gameobject.get_mono(Weapon)
            if weapon.owned:
                return
            self.weapons.append(weapon)
            weapon.owned = True
            GameEngineTools.DestroyObject(collider.gameobject)
            
    def on_notify(self,message):
        if message == 'dispatch':
            self.weapons = []
            