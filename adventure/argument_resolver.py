class ArgumentResolver:

	def init_data(self, data):
		self.data = data


	def get_resolver_function(self, resolver_function_name):
		return getattr(self, resolver_function_name, None)


	def execute(self, command, player, args):
		function = command.handler_function
		return function(player, self.get_first_arg(args))


	def resolve_movement(self, command, player, args):
		if args:
			return self.data.get_response("request_argless"), self.get_first_arg(args)
		return self.execute(command, player, [command.data_id])


	def resolve_switchable(self, command, player, args):
		arg = self.get_first_arg(args)
		if arg not in command.transitions:
			content = [command.primary] + sorted(list(command.transitions.keys()))
			return self.data.get_response("request_switch_command"), content
		transition = command.transitions[arg]
		return self.execute(command, player, [transition])


	def resolve_argless(self, command, player, args):
		if args:
			return self.data.get_response("request_argless"), self.get_first_arg(args)
		return self.execute(command, player, args)


	def resolve_args(self, command, player, args):
		if not args and not command.is_permissive():
			player.current_command = command
			return self.data.get_response("request_direct"), command.primary
		return self.resolve_args_for_item(command, player, args)


	def resolve_args_for_item(self, command, player, args):

		if not command.takes_item_arg(0):
			return self.execute(command, player, args)

		item = self.data.get_item(self.get_first_arg(args))
		if not item:
			return self.data.get_response("reject_unknown"), self.get_first_arg(args)

		return self.resolve_item_source(command, player, item, args[1:])


	def resolve_item_source(self, command, player, item, other_args):

		if command.takes_item_arg_from_inventory_only(0) and not player.is_carrying(item):
			return self.data.get_response("reject_not_holding"), item.shortname

		if command.takes_item_arg_from_location_only(0):
			if player.is_carrying(item):
				return self.data.get_response("reject_carrying"), item.shortname
			if not player.is_near_item(item):
				return self.data.get_response("reject_not_here"), item.shortname

		if command.takes_item_arg_from_inventory_or_location(0) and not player.has_or_is_near_item(item):
			return self.data.get_response("reject_not_here"), item.shortname

		return self.resolve_item_switch(command, player, item, other_args)



	def resolve_item_switch(self, command, player, item, switch_args):

		if command.is_switching():
			if not item.is_switchable():
				return self.data.get_response("reject_no_understand_instruction"), item.shortname

			transition_text = self.get_first_arg(switch_args)

			if not transition_text in item.text_to_transition:
				content = [item.shortname] + sorted(list(item.text_to_transition.keys()))
				return self.data.get_response("request_switch_item"), content

			transition = item.text_to_transition.get(transition_text)
			return command.handler_function(player, item, transition)

		return self.execute(command, player, [item])


	def get_first_arg(self, args):
		if args:
			return args[0]
		return None
