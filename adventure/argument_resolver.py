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


	def resolve_non_movement(self, command, player, arg):
		return self.execute(command, player, arg)
