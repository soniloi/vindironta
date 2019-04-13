from adventure.resolver import Resolver

class LifeResolver(Resolver):

	def resolve_life(self, command, player, *args):
		template_keys = []

		if not player.has_air():
			self.kill_non_immune_player(player, template_keys, "death_no_air")

		elif not player.has_tether():
			self.kill_non_immune_player(player, template_keys, "death_untethered")

		if player.is_alive():
			player.update_drop_location()
		else:
			player.drop_all_items()
			template_keys.append("describe_dead")
			template_keys.append("describe_reincarnation")

		return player.is_alive(), template_keys, [], list(args)


	def kill_non_immune_player(self, player, template_keys, death_template_key):
		if not player.is_immune():
			player.set_alive(False)
			template_keys.append(death_template_key)
