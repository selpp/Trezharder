from engine.core.monobehaviour import MonoBehaviour
from engine.core.game_engine import GameEngineTools
from engine.core.scene import SceneManager

class RestartTeamOut(MonoBehaviour):
	def __init__(self,teams_names):
		MonoBehaviour.__init__(self)
		self.teams_names = teams_names

	def start(self):
		self.teams = [GameEngineTools.find_all(self.teams_names[0]),GameEngineTools.find_all(self.teams_names[1])]

	def fixed_update(self,fdt):
		if self.should_restart():
			GameEngineTools.instance.model.update_training_variables()
			SceneManager.restart()

	def should_restart(self):
		for team in self.teams:
			if self.team_got_wipe_out(team):
				return True
		return False

	def team_got_wipe_out(self,team):
		for player in team:
				if player.is_alive:
					return False
		return True
