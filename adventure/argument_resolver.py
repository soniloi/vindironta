class ArgumentResolver:

	def init_data(self, data):
		self.data = data


	def get_resolver_function(self, resolver_function_name):
		return getattr(self, resolver_function_name, None)


	def execute(self, command, player, arg):
		function = command.handler_function
		return function(player, arg)


	def resolve_movement(self, command, player, arg):
		arg = command.command_id
		return self.execute(command, player, arg)


	def resolve_argless(self, command, player, arg):
		if arg:
			return self.data.responses.get("request_argless"), arg
		return self.execute(command, player, arg)


	def resolve_single_arg(self, command, player, arg):
		return self.execute(command, player, arg)
