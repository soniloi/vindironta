from adventure.resolver import Resolver

class LifeResolver(Resolver):

	def resolve_life(self, command, player, *args):
		template_keys = []

		if not player.has_air():
			player.set_alive(False)
			template_keys.append("death_no_air")

		if player.is_alive():
			player.update_drop_location()
		else:
			player.drop_all_items()
			template_keys.append("describe_dead")
			template_keys.append("describe_reincarnation")

		return player.is_alive(), template_keys, [], list(args)
