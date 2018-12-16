from adventure.resolver import Resolver

class PuzzleResolver(Resolver):

	def handle_say(self, command, player, word):
		return True, "", [word]
