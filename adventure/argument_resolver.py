from adventure.direction import Direction
from adventure.item import Item
from adventure.resolver import Resolver

class ArgumentResolver(Resolver):

	DIRECTIONS = {
		5 : Direction.BACK,
		13 : Direction.DOWN,
		16 : Direction.EAST,
		34 : Direction.NORTH,
		35 : Direction.NORTHEAST,
		36 : Direction.NORTHWEST,
		37 : Direction.OUT,
		52 : Direction.SOUTH,
		53 : Direction.SOUTHEAST,
		54 : Direction.SOUTHWEST,
		60 : Direction.UP,
		62 : Direction.WEST,
	}

	def resolve_teleport(self, command, player, *args):
		if args:
			return False, self.get_response("request_argless"), self.get_arg(0, args)

		source_location_id = player.get_location_id()
		if not source_location_id in command.teleport_locations:
			return False, self.get_response("reject_nothing"), [None]

		destination_location_id = command.teleport_locations[source_location_id]
		destination_location = self.data.get_location(destination_location_id)

		return True, "", [destination_location]


	def resolve_movement(self, command, player, *args):
		if args:
			return False, self.get_response("request_argless"), [self.get_arg(0, args)]

		direction = ArgumentResolver.DIRECTIONS[command.data_id]

		if direction == Direction.BACK:
			proposed_location = player.get_previous_location()
			if not proposed_location:
				return False, self.get_response("reject_no_back"), [direction]

		else:
			proposed_location = player.get_adjacent_location(direction)
			if not proposed_location:
				return False, self.get_reject_movement_template(direction), [direction]

		return True, "", [proposed_location]


	def get_reject_movement_template(self, direction):
		if direction == Direction.OUT:
			return self.get_response("reject_no_out")
		else:
			return self.get_response("reject_no_direction")


	def resolve_switchable(self, command, player, *args):
		arg = self.get_arg(0, args)
		if arg not in command.transitions:
			content = [command.primary] + sorted(list(command.transitions.keys()))
			return False, self.get_response("request_switch_command"), content

		transition = command.transitions[arg]
		return True, "", [transition]


	def resolve_switching(self, command, player, *args):
		arg_info = command.arg_infos[0]
		arg_input = self.get_arg(0, args)

		# Switching commands always take a single mandatory item argument
		if not arg_input:
			player.current_command = command
			player.current_args = []
			template, content = self.get_addinfo_response(command, [], None)
			return False, template, content

		success, template, content = self.resolve_arg_for_command(command, player, arg_info, arg_input)

		if not success:
			player.reset_current_command()
			return False, template, content

		item = content
		switch_args = args[1:]

		if not item.is_switchable():
			return False, self.get_response("reject_no_understand_instruction"), [item.shortname]

		transition_text = self.get_arg(0, switch_args)

		if not transition_text in item.text_to_transition:
			content = [item.shortname] + sorted(list(item.text_to_transition.keys()))
			return False, self.get_response("request_switch_item"), content

		transition = item.text_to_transition.get(transition_text)
		player.reset_current_command()
		return True, "", [item, transition]


	def resolve_args(self, command, player, *args):

		resolved_args = player.get_current_args()
		arg_input_offset = len(resolved_args)

		# TODO: fix the flow control here
		input_index = 0
		for i in range(arg_input_offset, len(command.arg_infos)):

			arg_info = command.arg_infos[i]
			arg_input = self.get_arg(input_index, args)
			input_index += 1

			arg_expected = False
			current_linker = None
			if arg_info.is_valid_linker(arg_input):
				current_linker = arg_input
				arg_input = self.get_arg(input_index, args)
				arg_expected = True
				input_index += 1

			if not arg_input:
				if arg_expected or arg_info.mandatory:
					player.current_command = command
					player.current_args = resolved_args
					# TODO: improve this to request non-direct args properly also
					template, content = self.get_addinfo_response(command, resolved_args, current_linker)
					return False, template, content

			else:
				success, template, content = self.resolve_arg_for_command(command, player, arg_info, arg_input)

				if not success:
					player.reset_current_command()
					return False, template, content
				resolved_args.append(content)

		player.reset_current_command()
		return True, "", resolved_args


	def get_arg(self, index, args):
		if index < len(args):
			return args[index]
		return None


	def get_addinfo_response(self, command, resolved_args, given_linker):
		template = self.get_response("request_addinfo")
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
			return True, "", arg_input

		item = self.data.get_item(arg_input)
		if not item:
			return False, self.get_response("reject_unknown"), [arg_input]

		carried_item = player.get_carried_item(item)
		nearby_item = player.get_nearby_item(item)

		if arg_info.takes_item_arg_from_inventory_only():
			if not carried_item:
				return False, self.get_response("reject_not_holding"), [item.shortname]
			item = carried_item

		if arg_info.takes_item_arg_from_location_only():
			if carried_item:
				return False, self.get_response("reject_carrying"), [item.shortname]
			if not nearby_item:
				return False, self.get_response("reject_not_here"), [item.shortname]
			item = nearby_item

		if arg_info.takes_item_arg_from_inventory_or_location():
			if not carried_item and not nearby_item:
				return False, self.get_response("reject_not_here"), [item.shortname]
			# TODO: determine the ordering here
			item = carried_item
			if not item:
				item = nearby_item

		return True, "", item
