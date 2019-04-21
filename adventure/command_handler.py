from adventure.direction import Direction
from adventure.item import Item, SwitchTransition
from adventure.resolver import Resolver

class CommandHandler(Resolver):

	# TODO: find a place for this
	POINTS_PER_PUZZLE = 7

	def handle_burn(self, command, player, item):
		if not item.is_burnable():
			return False, ["reject_not_burnable"], [item], []

		if not player.can_burn():
			return False, ["reject_cannot_burn"], [item], []

		return self.replace_item(command, item, "confirm_burn")


	def handle_climb(self, command, player, arg=None):
		return False, ["reject_climb"], [], []


	def handle_commands(self, command, player):
		return True, ["describe_commands"], [self.data.list_commands()], []


	def handle_consume(self, command, player, item):
		content_args = [item]

		if not item.is_edible():
			return False, ["reject_not_consumable"], content_args, []

		item.destroy()
		return True, ["confirm_consume"], content_args, [item]


	def handle_describe(self, command, player, item):
		template_keys = ["describe_item"]
		if item.is_switchable():
			template_keys.append("describe_item_switch")
		return True, template_keys, item.get_full_description(), [item]


	def handle_disembark(self, command, player, item):
		if not item.is_sailable():
			return False, ["reject_not_sailable"], [item], []

		if not item.being_used:
			return False, ["reject_not_sailing"], [item], []

		item.being_used = False
		return True, ["confirm_disembark"], [item], [item]


	def handle_drink(self, command, player, item):
		if not item.is_liquid():
			return False, ["reject_drink_solid"], [item], []

		return self.handle_consume(command, player, item)


	def handle_drop(self, command, player, item):
		content_args = [item]
		next_args = [item]

		if item.is_liquid():
			content_args.append(item.get_first_container())
			item.destroy()
			return True, ["confirm_poured_no_destination"], content_args, next_args

		dropped_item = item
		template_keys = ["confirm_dropped"]
		location = player.get_location()
		destination = location.get_drop_location()

		if destination is not location:
			template_keys.append("describe_item_falling")
			if item.is_fragile():
				template_keys.append("describe_item_smash_hear")
				dropped_item = self.break_item(item, destination, template_keys, content_args)

		dropped_item.remove_from_containers()

		if destination.has_land():
			destination.insert(dropped_item)
		else:
			item.destroy()
			template_keys.append("describe_item_sink")

		return True, template_keys, content_args, next_args


	def break_item(self, item, destination, template_keys, content_args):
		item_within = item.break_open()
		dropped_item = item.replacements[Item.COMMAND_ID_SMASH]
		content_args.append(dropped_item)

		if item_within:
			content_args.append(item_within)
			if item_within.is_liquid():
				template_keys.append("describe_item_smash_release_liquid")
			else:
				destination.insert(item_within)
				template_keys.append("describe_item_smash_release_solid")

		return dropped_item


	def handle_eat(self, command, player, item):
		if item.is_liquid():
			return False, ["reject_eat_liquid"], [item], []

		return self.handle_consume(command, player, item)


	def handle_empty(self, command, player, item):
		content_args = [item]
		next_args = [item]

		if not item.is_container():
			return False, ["reject_not_container"], content_args, []

		if not item.has_items():
			return False, ["reject_already_empty"], content_args, []

		contained_item = item.get_contained_item()
		content_args.append(contained_item)
		item.remove(contained_item)

		if item.is_liquid_container():
			contained_item.destroy()
			return True, ["confirm_emptied_liquid"], content_args, next_args

		outermost_item = item.get_outermost_container()
		outermost_item.insert(contained_item)
		return True, ["confirm_emptied_solid"], content_args, next_args


	def handle_explain(self, command, player, arg):
		explanation = self.data.get_explanation(arg)

		if not explanation:
			return False, [self.data.get_explanation("default")], [arg], []

		return True, [explanation], [arg], [arg]


	def handle_feed(self, command, player, proposed_gift, proposed_recipient):
		content_args = [proposed_gift, proposed_recipient]

		if not proposed_recipient.is_sentient():
			return False, ["reject_give_inanimate"], content_args, []

		if not proposed_gift.is_edible():
			return False, ["reject_not_consumable"], content_args, []

		proposed_gift.destroy()
		return True, ["confirm_feed"], content_args, [proposed_gift, proposed_recipient]


	def handle_free(self, command, player, item):
		return self.handle_drop(command, player, item)


	def handle_give(self, command, player, proposed_gift, proposed_recipient):
		content_args = [proposed_gift, proposed_recipient]

		if not proposed_recipient.is_sentient():
			return False, ["reject_give_inanimate"], content_args, []

		if proposed_gift.is_liquid():
			return False, ["reject_give_liquid"], content_args, []

		proposed_gift.remove_from_containers()
		proposed_recipient.insert(proposed_gift)
		return True, ["confirm_given"], content_args, [proposed_gift, proposed_recipient]


	def handle_go(self, command, player, direction, proposed_location):
		obstructions = player.get_obstructions()
		if obstructions and proposed_location is not player.get_previous_location():
			template_key, content = self.reject_go_obstructed(player, obstructions)
			return False, [template_key], content, []

		current_location = player.get_location()
		environment_movement_reject_template = self.get_environment_movement_reject_template(
			player, current_location, proposed_location, direction)
		if environment_movement_reject_template:
			return False, [environment_movement_reject_template], [], []

		self.update_previous_location(player, proposed_location)
		player.location = proposed_location

		return True, [], [], [proposed_location, current_location]


	def reject_go_obstructed(self, player, obstructions):
		# TODO: move into vision resolver
		if player.has_light():
			return "reject_obstruction_known", [obstructions[0].longname]
		return "reject_obstruction_unknown", []


	def get_environment_movement_reject_template(self, player, current_location, proposed_location, direction):
		if player.is_immune():
			return None

		if not proposed_location.gives_air() and not player.carries_air():
			return "reject_movement_no_air"

		if not proposed_location.has_land() and not player.carries_land():
			return "reject_movement_no_land"

		if direction == Direction.DOWN and not current_location.has_floor():
			return "reject_movement_no_floor"

		return None


	def update_previous_location(self, player, proposed_location):
		if proposed_location.can_reach(player.location):
			player.set_previous_location(player.location)
		else:
			player.set_previous_location(None)


	def handle_go_disambiguate(self, command, player, arg):
		return False, ["reject_go"], [], []


	def handle_help(self, command, player):
		player.decrement_instructions()
		return True, ["describe_help"], [], []


	def handle_hint(self, command, player, arg):
		hint = self.data.get_hint(arg)

		if not hint:
			return False, [self.data.get_hint("default")], [arg], []

		return True, [hint], [arg], [arg]


	def handle_immune(self, command, player, arg):
		template_key = ""

		player.set_immune(arg)
		if arg:
			template_key = "confirm_immune_on"
		else:
			template_key = "confirm_immune_off"

		return True, [template_key], [arg], [arg]


	def handle_insert(self, command, player, item, proposed_container):
		content_args = [item, proposed_container]

		if not proposed_container.is_container():
			return False, ["reject_not_container"], content_args, []

		if item is proposed_container:
			return False, ["reject_container_self"], content_args, []

		if proposed_container in item.containers:
			return False, ["reject_already_contained"], content_args, []

		if not item.is_portable():
			return False, ["reject_not_portable"], content_args, []

		if item.is_liquid() and not proposed_container.is_liquid_container():
			return False, ["reject_insert_liquid"], content_args, []

		if not item.is_liquid() and proposed_container.is_liquid_container():
			return False, ["reject_insert_solid"], content_args, []

		if proposed_container.has_items():
			return False, ["reject_not_empty"], content_args, []

		if not proposed_container.can_accommodate(item):
			return False, ["reject_container_size"], content_args, []

		if not item.is_copyable():
			item.remove_from_containers()
		proposed_container.insert(item)

		return True, ["confirm_inserted"], content_args, [item, proposed_container]


	def handle_inventory(self, command, player):
		if not player.holding_items():
			return True, ["list_inventory_empty"], [], []
		return True, ["list_inventory_nonempty"], [player.describe_inventory()], []


	def handle_locate(self, command, player, item):
		template_keys = ["describe_locate_primary"]
		primary_containers = item.containers
		primary_container_descriptions = [str(container.data_id) + ":" + container.longname for container in primary_containers]
		content_args = [item.shortname, str(primary_container_descriptions)]
		next_args = [item]

		item_copies = item.copied_to
		copy_container_descriptions = []
		for item_copy in item_copies:
			copy_container = item_copy.get_first_container()
			copy_container_descriptions.append(str(copy_container.data_id) + ":" + copy_container.longname)

		if copy_container_descriptions:
			template_keys.append("describe_locate_copies")
			content_args.append(str(copy_container_descriptions))

		return True, template_keys, content_args, next_args


	def handle_look(self, command, player):
		template_keys = ["describe_location"]

		if player.has_non_silent_items_nearby():
			template_keys.append("list_location")

		return True, template_keys, player.get_full_location_description(), []


	def handle_node(self, command, player, arg=None):
		if not arg:
			return False, ["describe_node"], [player.location.data_id], []

		location_id = player.location.data_id
		try:
			location_id = int(arg)
			proposed_location = self.data.get_location(location_id)
			if proposed_location:
				current_location = player.location
				player.location = proposed_location
				return True, [], [], [proposed_location, current_location]
		except:
			pass

		return False, ["reject_no_node"], [arg], []


	def handle_pick(self, command, player, item):
		return self.handle_take(command, player, item)


	def handle_pour(self, command, player, item, destination):
		content_args = [item]
		next_args = [item, destination]

		if not item.is_liquid():
			return False, ["reject_not_liquid"], content_args, []

		source = item.get_first_container()
		item.destroy()
		content_args.extend([destination, source])

		return True, ["confirm_poured_with_destination"], content_args, next_args


	def handle_quit(self, command, player):
		player.decrement_instructions()
		player.set_playing(False)
		return True, ["confirm_quit"], [], []


	def handle_read(self, command, player, item):
		if not item.writing:
			return False, ["reject_no_writing"], [item], []
		return True, ["describe_writing"], [item.writing], [item]


	def handle_rub(self, command, player, item):
		return True, [], [], [item]


	def handle_sail(self, command, player, item):
		if not item.is_sailable():
			return False, ["reject_not_sailable"], [item], []

		location = player.get_location()
		if not location.has_water():
			return False, ["reject_no_water_sail"], [item], []

		if item.being_used:
			return False, ["reject_already_sailing"], [item], []

		item.being_used = True
		return True, ["confirm_sail"], [item], [item]


	def handle_say(self, command, player, word, audience=None):
		content_args = [word]
		next_args = [word]

		if not audience:
			return True, ["confirm_say_no_audience"], content_args, next_args

		content_args.append(audience)
		next_args.append(audience)

		if not audience.is_sentient():
			return True, ["confirm_say_no_sentient_audience"], content_args, next_args

		return True, ["confirm_say_audience"], content_args, next_args


	def handle_score(self, command, player):
		player.decrement_instructions()
		current_score = player.count_solved_puzzles() * CommandHandler.POINTS_PER_PUZZLE
		maximum_score = self.data.get_puzzle_count() * CommandHandler.POINTS_PER_PUZZLE
		current_instructions = player.instructions
		return True, ["describe_score"], [current_score, maximum_score, current_instructions], []


	def handle_set(self, command, player, item):
		return self.handle_drop(command, player, item)


	def handle_smash(self, command, player, item):
		if not item.is_smashable():
			return False, ["reject_not_smashable"], [item], []

		if item.is_strong() and not player.is_strong():
			return False, ["reject_not_strong"], [item], []

		return self.replace_item(command, item, "confirm_smash")


	def handle_switch(self, command, player, item, transition):
		if transition == SwitchTransition.OFF:
			if not item.is_on():
				return False, ["reject_already_switched"], [item, item.get_state_text()], []
			item.switch_off()

		elif transition == SwitchTransition.ON:
			if item.is_on():
				return False, ["reject_already_switched"], [item, item.get_state_text()], []
			item.switch_on()

		elif transition == SwitchTransition.TOGGLE:
			item.switch_toggle()

		return True, ["describe_switch_item"], [item, item.get_state_text()], [item, transition]


	def handle_take(self, command, player, item, proposed_container=None):
		content_args = [item]

		owner = item.get_sentient_owner()
		if owner:
			content_args.append(owner)
			return False, ["reject_take_animate"], content_args, []

		if proposed_container:
			return self.handle_insert(command, player, item, proposed_container)

		if not item.is_portable():
			return False, ["reject_not_portable"], content_args, []

		if item.is_liquid():
			return False, ["reject_take_liquid"], content_args, []

		if not player.can_carry(item):
			return False, ["reject_too_full"], content_args, []

		player.take_item(item)
		next_args = [item]
		if proposed_container:
			next_args.append(proposed_container)

		return True, ["confirm_taken"], content_args, next_args


	def handle_teleport(self, command, player, destination):
		source = player.location
		player.location = destination
		return True, [], [], [destination, source]


	def handle_throw(self, command, player, item):
		content_args = [item]
		next_args = [item]

		if item.is_liquid():
			return False, ["reject_throw_liquid"], content_args, []

		dropped_item = item
		template_keys = ["confirm_throw"]
		location = player.get_location()
		destination = location
		if not location.has_floor():
			destination = destination.get_adjacent_location(Direction.DOWN)
			template_keys.append("describe_item_falling")

		if item.is_fragile():
			if location.has_floor():
				template_keys.append("describe_item_smash_see")
			else:
				template_keys.append("describe_item_smash_hear")

			dropped_item = self.break_item(item, destination, template_keys, content_args)

		dropped_item.remove_from_containers()

		if destination.has_land():
			destination.insert(dropped_item)
		else:
			item.destroy()
			template_keys.append("describe_item_sink")

		return True, template_keys, content_args, next_args


	def handle_toggle(self, command, player, item):
		if not item.is_switchable():
			return False, ["reject_no_know_how"], [item], []
		return self.handle_switch(command, player, item, SwitchTransition.TOGGLE)


	def handle_verbose(self, command, player, arg):
		template_key = []

		player.set_verbose(arg)
		if arg:
			template_key = "confirm_verbose_on"
		else:
			template_key = "confirm_verbose_off"

		return True, [template_key], [arg], [arg]


	def handle_wear(self, command, player, item):
		if not item.is_wearable():
			return False, ["reject_not_wearable"], [item], []

		if item.being_used:
			return False, ["reject_already_wearing"], [item], []

		player.take_item(item)
		item.being_used = True
		return True, ["confirm_wearing"], [item], [item]


	def replace_item(self, command, item, confirm_text_key):
		replacement = item.replacements[command.data_id]
		container = item.get_first_container()
		item.destroy()
		container.insert(replacement)

		return True, [confirm_text_key], [item, replacement], [item]
