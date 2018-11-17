from adventure.item import Item

class ArgumentResolver:

	def init_data(self, data):
		self.data = data


	def get_resolver_function(self, resolver_function_name):
		return getattr(self, resolver_function_name, None)


	def execute(self, command, player, args):
		function = command.handler_function
		return function(player, *args)


	def resolve_movement(self, command, player, args):
		if args:
			return self.data.get_response("request_argless"), self.get_arg(args, 0)
		return self.execute(command, player, [command.data_id])


	def resolve_switchable(self, command, player, args):
		arg = self.get_arg(args, 0)
		if arg not in command.transitions:
			content = [command.primary] + sorted(list(command.transitions.keys()))
			return self.data.get_response("request_switch_command"), content
		transition = command.transitions[arg]
		return self.execute(command, player, [transition])


	def resolve_argless(self, command, player, args):
		if args:
			return self.data.get_response("request_argless"), self.get_arg(args, 0)
		return self.execute(command, player, args)


	def resolve_args(self, command, player, args):

		resolved_args = player.get_current_args()
		arg_input_offset = len(resolved_args)

		# TODO: fix the flow control here
		input_index = 0
		for i in range(arg_input_offset, len(command.arg_infos)):

			arg_info = command.arg_infos[i]
			arg_input = self.get_arg(args, input_index)
			input_index += 1

			if arg_info.is_valid_linker(arg_input):
				arg_input = self.get_arg(args, input_index)
				input_index += 1

			if not arg_input:
				if arg_info.mandatory:
					player.current_command = command
					player.current_args = resolved_args
					# TODO: improve this to request non-direct args properly also
					template, content = self.get_addinfo_response(command, resolved_args)
					return template, content

			else:
				success, response = self.resolve_arg_for_command(command, player, arg_info, arg_input)

				if not success:
					player.reset_current_command()
					return response
				resolved_args.append(response)

		response = ""
		if command.is_switching():
			response =  self.execute_switching(command, player, resolved_args[0], resolved_args[1:])
		else:
			response = self.execute(command, player, resolved_args)

		player.reset_current_command()
		return response


	def get_arg(self, args, index):
		if index < len(args):
			return args[index]
		return None


	def get_addinfo_response(self, command, resolved_args):
		template = self.data.get_response("request_addinfo")
		verb = command.primary
		arg_infos = command.arg_infos

		noun_content = ""
		if resolved_args:
			noun_content = self.get_addinfo_noun_content(resolved_args, arg_infos)

		content = [verb, noun_content]
		return template, content


	def get_addinfo_noun_content(self, resolved_args, arg_infos):
		noun_tokens = []

		for i in range(0, len(resolved_args)):
			arg = resolved_args[i]
			linker = arg_infos[i+1].primary_linker

			if isinstance(arg, Item):
				noun_tokens.append(arg.shortname)
			else:
				noun_tokens.append(arg)

			if linker:
				noun_tokens.append(linker)

		return " " + " ".join(noun_tokens)


	def resolve_arg_for_command(self, command, player, arg_info, arg_input):
		if not arg_info.is_item:
			return True, arg_input

		item = self.data.get_item(arg_input)
		if not item:
			return False, (self.data.get_response("reject_unknown"), arg_input)

		if arg_info.takes_item_arg_from_inventory_only() and not player.is_carrying(item):
			return False, (self.data.get_response("reject_not_holding"), item.shortname)

		if arg_info.takes_item_arg_from_location_only():
			if player.is_carrying(item):
				return False, (self.data.get_response("reject_carrying"), item.shortname)
			if not player.is_near_item(item):
				return False, (self.data.get_response("reject_not_here"), item.shortname)

		if arg_info.takes_item_arg_from_inventory_or_location() and not player.has_or_is_near_item(item):
			return False, (self.data.get_response("reject_not_here"), item.shortname)

		return True, item


	def execute_switching(self, command, player, item, switch_args):

		if not item.is_switchable():
			return self.data.get_response("reject_no_understand_instruction"), item.shortname

		transition_text = self.get_arg(switch_args, 0)

		if not transition_text in item.text_to_transition:
			content = [item.shortname] + sorted(list(item.text_to_transition.keys()))
			return self.data.get_response("request_switch_item"), content

		transition = item.text_to_transition.get(transition_text)
		return command.handler_function(player, item, transition)
