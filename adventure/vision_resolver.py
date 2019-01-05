from adventure.resolver import Resolver

class VisionResolver(Resolver):

	def resolve_pre_light_and_dark(self, command, player, *args):

		if player.has_light_and_needs_no_light():
			return False, self.get_response("reject_excess_light"), [], []

		elif not player.has_light():
			return False, self.get_response("reject_no_light"), [], []

		return True, "", [], list(args)


	def resolve_pre_dark(self, command, player, *args):

		if not player.has_light():
			return False, self.get_response("reject_no_light"), [], []

		return True, "", [], list(args)


	def resolve_post_light_and_dark(self, command, player, new_location, previous_location):

		if not player.is_immune() and not player.has_light() and not previous_location.gives_light():
			self.kill_player(player, previous_location)
			return False, self.get_response("death_darkness"), [], []

		if player.has_light_and_needs_no_light():
			return False, self.get_response("reject_excess_light"), [], []

		if not player.has_light():
			return False, self.get_response("reject_no_light"), [], []

		template = self.get_response("confirm_look")
		if player.has_non_silent_items_nearby():
			template += self.get_response("list_location")

		content_args = player.get_arrival_location_description()
		player.see_location()

		return True, template, content_args, [new_location, previous_location]


	def kill_player(self, player, previous_location):
		player.set_alive(False)
		player.drop_all_items(previous_location)
