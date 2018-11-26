from adventure.item import Item
from adventure.resolver import Resolver

class ArgumentResolver(Resolver):

	def resolve_teleport(self, command, player, args):
		if args:
			return False, (self.data.get_response("request_argless"), self.get_arg(args, 0))

		source_location_id = player.get_location_id()
		if not source_location_id in command.teleport_locations:
			return False, (self.data.get_response("reject_nothing"), [None])

		destination_location_id = command.teleport_locations[source_location_id]
		destination_location = self.data.get_location(destination_location_id)

		return True, (player, [destination_location])


	def resolve_movement(self, command, player, args):
		if args:
			return False, (self.data.get_response("request_argless"), [self.get_arg(args, 0)])
		return True, (player, [command.data_id])


	def resolve_switchable(self, command, player, args):
		arg = self.get_arg(args, 0)
		if arg not in command.transitions:
			content = [command.primary] + sorted(list(command.transitions.keys()))
			return False, (self.data.get_response("request_switch_command"), content)

		transition = command.transitions[arg]
		return True, (player, [transition])


	def resolve_switching(self, command, player, args):
		arg_info = command.arg_infos[0]
		arg_input = self.get_arg(args, 0)

		# Switching commands always take a single mandatory item argument
		if not arg_input:
			player.current_command = command
			player.current_args = []
			template, content = self.get_addinfo_response(command, [], None)
			return False, (template, content)

		success, response = self.resolve_arg_for_command(command, player, arg_info, arg_input)

		if not success:
			player.reset_current_command()
			return False, response

		item = response
		switch_args = args[1:]

		if not item.is_switchable():
			return False, (self.data.get_response("reject_no_understand_instruction"), [item.shortname])

		transition_text = self.get_arg(switch_args, 0)

		if not transition_text in item.text_to_transition:
			content = [item.shortname] + sorted(list(item.text_to_transition.keys()))
			return False, (self.data.get_response("request_switch_item"), content)

		transition = item.text_to_transition.get(transition_text)
		player.reset_current_command()
		return True, (player, [item, transition])


	def resolve_args(self, command, player, args):

		resolved_args = player.get_current_args()
		arg_input_offset = len(resolved_args)

		# TODO: fix the flow control here
		input_index = 0
		for i in range(arg_input_offset, len(command.arg_infos)):

			arg_info = command.arg_infos[i]
			arg_input = self.get_arg(args, input_index)
			input_index += 1

			current_linker = None
			if arg_info.is_valid_linker(arg_input):
				current_linker = arg_input
				arg_input = self.get_arg(args, input_index)
				input_index += 1

			if not arg_input:
				if arg_info.mandatory:
					player.current_command = command
					player.current_args = resolved_args
					# TODO: improve this to request non-direct args properly also
					template, content = self.get_addinfo_response(command, resolved_args, current_linker)
					return False, (template, content)

			else:
				success, response = self.resolve_arg_for_command(command, player, arg_info, arg_input)

				if not success:
					player.reset_current_command()
					return False, response
				resolved_args.append(response)

		player.reset_current_command()
		return True, (player, resolved_args)


	def get_arg(self, args, index):
		if index < len(args):
			return args[index]
		return None


	def get_addinfo_response(self, command, resolved_args, given_linker):
		template = self.data.get_response("request_addinfo")
		verb = command.primary
		arg_infos = command.arg_infos

		noun_content = ""
		if resolved_args:
			noun_content = self.get_addinfo_noun_content(resolved_args, arg_infos, given_linker)

		content = [verb, noun_content]
		return template, content


	def get_addinfo_noun_content(self, resolved_args, arg_infos, given_linker):
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

		if given_linker:
			noun_tokens[-1] = given_linker

		return " " + " ".join(noun_tokens)


	def resolve_arg_for_command(self, command, player, arg_info, arg_input):
		if not arg_info.is_item:
			return True, arg_input

		item = self.data.get_item(arg_input)
		if not item:
			return False, (self.data.get_response("reject_unknown"), [arg_input])

		if arg_info.takes_item_arg_from_inventory_only() and not player.is_carrying(item):
			return False, (self.data.get_response("reject_not_holding"), [item.shortname])

		if arg_info.takes_item_arg_from_location_only():
			if player.is_carrying(item):
				return False, (self.data.get_response("reject_carrying"), [item.shortname])
			if not player.is_near_item(item):
				return False, (self.data.get_response("reject_not_here"), [item.shortname])

		if arg_info.takes_item_arg_from_inventory_or_location() and not player.has_or_is_near_item(item):
			return False, (self.data.get_response("reject_not_here"), [item.shortname])

		return True, item


	def execute_switching(self, command, player, item, switch_args):

		if not item.is_switchable():
			return False, (self.data.get_response("reject_no_understand_instruction"), item.shortname)

		transition_text = self.get_arg(switch_args, 0)

		if not transition_text in item.text_to_transition:
			content = [item.shortname] + sorted(list(item.text_to_transition.keys()))
			return False, (self.data.get_response("request_switch_item"), content)

		transition = item.text_to_transition.get(transition_text)
		return True, (player, [item, transition])
