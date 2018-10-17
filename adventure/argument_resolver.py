class ArgumentResolver:

	def init_data(self, data):
		self.data = data


	def get_resolver_function(self, resolver_function_name):
		return getattr(self, resolver_function_name, None)


	def execute(self, command, player, arg):
		function = command.handler_function
		return function(player, arg)


	def resolve_movement(self, command, player, arg):
		if arg:
			return self.data.get_response("request_argless"), arg
		return self.execute(command, player, command.command_id)


	def resolve_switchable(self, command, player, arg):
		if arg not in command.transitions:
			content = [command.primary] + sorted(list(command.transitions.keys()))
			return self.data.get_response("request_switch"), content
		next_state = command.transitions[arg]
		return self.execute(command, player, next_state)


	def resolve_argless(self, command, player, arg):
		if arg:
			return self.data.get_response("request_argless"), arg
		return self.execute(command, player, arg)


	def resolve_single_arg(self, command, player, arg):
		if not arg and not command.is_permissive():
			player.current_command = command
			return self.data.get_response("request_direct"), command.primary
		return self.resolve_single_arg_for_item(command, player, arg)


	def resolve_single_arg_for_item(self, command, player, arg):
		if command.takes_item_arg():
			item = self.data.get_item(arg)
			if not item:
				return self.data.get_response("reject_unknown"), arg
			arg = item
		return self.execute(command, player, arg)
