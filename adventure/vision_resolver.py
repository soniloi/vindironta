from adventure.resolver import Resolver

class VisionResolver(Resolver):

	def resolve_light_and_dark(self, command, player, *args):

		if player.has_light_and_needs_no_light():
			return False, self.data.get_response("reject_excess_light"), []

		elif not player.has_light():
			return False, self.data.get_response("reject_no_light"), []

		return True, "", list(args)


	def resolve_dark(self, command, player, *args):

		if not player.has_light():
			return False, self.data.get_response("reject_no_light"), []

		return True, "", list(args)
