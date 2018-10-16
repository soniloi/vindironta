class VisionResolver:

	def init_data(self, data):
		self.data = data


	def get_resolver_function(self, resolver_function_name):
		return getattr(self, resolver_function_name, None)


	def resolve(self, command, player, arg):
		return command.arg_function(command, player, arg)


	def resolve_light_and_dark(self, command, player, arg):

		if player.has_light_and_needs_no_light():
			return self.data.get_response("reject_excess_light"), ""

		elif not player.has_light():
			return self.data.get_response("reject_no_light"), ""

		return self.resolve(command, player, arg)


	def resolve_dark(self, command, player, arg):

		if not player.has_light():
			return self.data.get_response("reject_no_light"), ""

		return self.resolve(command, player, arg)


	def resolve_none(self, command, player, arg):
		return self.resolve(command, player, arg)
