from adventure.resolver import Resolver

class VisionResolver(Resolver):

	def resolve_pre_light_and_dark(self, command, player, *args):

		if player.has_light_and_needs_no_light():
			return False, ["reject_excess_light"], [], []

		elif not player.has_light():
			return False, ["reject_no_light"], [], []

		return True, [], [], list(args)


	def resolve_pre_dark(self, command, player, *args):

		if not player.has_light():
			return False, ["reject_no_light"], [], []

		return True, [], [], list(args)


	def resolve_post_light_and_dark(self, command, player, new_location, previous_location):

		if not player.is_immune() and not player.has_light() and not previous_location.gives_light():
			player.set_alive(False)
			return True, ["death_darkness"], [], []

		if player.has_light_and_needs_no_light():
			return True, ["reject_excess_light"], [], []

		if not player.has_light():
			return True, ["reject_no_light"], [], []

		template_keys = ["confirm_look"]
		if player.has_non_silent_items_nearby():
			template_keys.append("list_location")

		content_args = player.get_arrival_location_description()
		player.see_location()

		return True, template_keys, content_args, [new_location, previous_location]
