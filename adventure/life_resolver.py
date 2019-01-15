from adventure.resolver import Resolver

class LifeResolver(Resolver):

	def resolve_life(self, command, player, *args):
		templates = []

		if not player.has_air():
			player.set_alive(False)
			templates.append(self.data.get_response("death_no_air"))

		if not player.is_alive():
			templates.append(self.data.get_response("describe_dead"))
			templates.append(self.data.get_response("describe_reincarnation"))

		return player.is_alive(), templates, [], list(args)
