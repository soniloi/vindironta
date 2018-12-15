from adventure.direction import Direction
from adventure.inventory import Inventory
from adventure.item import SwitchTransition

class CommandHandler:

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

	def init_data(self, data):
		self.data = data


	def get_handler_function(self, function_name):
		return getattr(self, function_name, None)


	def get_response(self, response_key):
		return self.data.get_response(response_key)


	def handle_climb(self, command, player, arg=None):
		return False, self.get_response("reject_climb"), [""]


	def handle_commands(self, command, player):
		template = self.get_response("describe_commands")
		content = [self.data.list_commands()]
		return True, template, content


	def handle_consume(self, command, player, item):
		if not item.is_edible():
			return False, self.get_response("reject_not_consumable"), [item]

		item.destroy()
		return True, self.get_response("confirm_consume"), [item]


	def handle_describe(self, command, player, item):
		template = self.get_response("describe_item")
		if item.is_switchable():
			template += self.get_response("describe_item_switch")
		return True, template, item.get_full_description()


	def handle_drink(self, command, player, item):
		if not item.is_liquid():
			return False, self.get_response("reject_drink_solid"), [item]

		return self.handle_consume(command, player, item)


	def handle_drop(self, command, player, item):
		if item.is_liquid():
			item_source = item.get_first_container()
			item.destroy()
			return True, self.get_response("confirm_poured_no_destination"), [item, item_source]

		player.drop_item(item)
		return True, self.get_response("confirm_dropped"), [item]


	def handle_eat(self, command, player, item):
		if item.is_liquid():
			return False, self.get_response("reject_eat_liquid"), [item]

		return self.handle_consume(command, player, item)


	def handle_empty(self, command, player, item):
		content = [item]
		if not item.is_container():
			return False, self.get_response("reject_not_container"), content

		if not item.has_items():
			return False, self.get_response("reject_already_empty"), content

		contained_item = item.get_contained_item()
		content.append(contained_item)
		item.remove(contained_item)

		if item.is_liquid_container():
			contained_item.destroy()
			return True, self.get_response("confirm_emptied_liquid"), content

		outermost_item = item.get_outermost_container()
		outermost_item.insert(contained_item)
		return True, self.get_response("confirm_emptied_solid"), content


	def handle_explain(self, command, player, arg):
		template = self.data.get_explanation(arg)

		if not template:
			template = self.data.get_explanation("default")

		return True, template, [arg]


	def handle_feed(self, command, player, proposed_gift, proposed_recipient):

		content = [proposed_gift, proposed_recipient]

		if not proposed_recipient.is_sentient():
			return False, self.get_response("reject_give_inanimate"), content

		if not proposed_gift.is_edible():
			return False, self.get_response("reject_not_consumable"), content

		proposed_gift.destroy()
		return True, self.get_response("confirm_feed"), content


	def handle_give(self, command, player, proposed_gift, proposed_recipient):

		content = [proposed_gift, proposed_recipient]

		if not proposed_recipient.is_sentient():
			return False, self.get_response("reject_give_inanimate"), content

		if proposed_gift.is_liquid():
			return False, self.get_response("reject_give_liquid"), content

		proposed_gift.remove_from_containers()
		proposed_recipient.insert(proposed_gift)
		return True, self.get_response("confirm_given"), content


	def handle_go(self, command, player, arg):
		direction = CommandHandler.DIRECTIONS[arg]

		proposed_location, reject_template_key = self.get_proposed_location_and_reject_key(player, direction)
		template = self.get_response(reject_template_key)
		content = [""]

		if proposed_location:
			template, content = self.execute_go_if_not_obstructed(player, arg, proposed_location)

		# TODO: fix success indicator
		return True, template, content


	def get_proposed_location_and_reject_key(self, player, direction):
		if direction == Direction.BACK:
			return player.previous_location, "reject_no_back"

		return player.get_adjacent_location(direction), self.get_non_back_reject_key(direction)


	def get_non_back_reject_key(self, direction):
		if direction == Direction.OUT:
			return "reject_no_out"
		return "reject_no_direction"


	def execute_go_if_not_obstructed(self, player, arg, proposed_location):
		obstructions = player.get_obstructions()
		content = [""]

		if obstructions and proposed_location is not player.previous_location:
			template_key, content = self.reject_go_obstructed(player, obstructions)
			template = self.get_response(template_key)

		elif not player.has_light() and not proposed_location.gives_light() and not player.immune:
			self.kill_player(player)
			template = self.get_response("death_darkness")

		else:
			self.update_previous_location(player, proposed_location)
			template, content = self.execute_go(player, arg, proposed_location)
			self.interact_vision(player, arg, self.execute_see_location)

		return template, content


	def kill_player(self, player):
		player.alive = False
		player.drop_all_items()


	def reject_go_obstructed(self, player, obstructions):
		if player.has_light():
			return "reject_obstruction_known", [obstructions[0].longname]
		return "reject_obstruction_unknown", [""]


	def update_previous_location(self, player, proposed_location):
		if proposed_location.can_reach(player.location):
			player.previous_location = player.location
		else:
			player.previous_location = None


	def execute_go(self, player, arg, proposed_location):
		player.location = proposed_location
		return self.interact_vision(player, arg, self.complete_go)


	def complete_go(self, player, arg):
		template = self.get_response("confirm_look")
		if player.has_non_silent_items_nearby():
			template += self.get_response("list_location")

		return template, player.get_arrival_location_description()


	def execute_see_location(self, player, arg):
		player.see_location()


	def handle_go_disambiguate(self, command, player, arg):
		return False, self.get_response("reject_go"), [""]


	def handle_help(self, command, player, arg):
		player.decrement_instructions()
		return True, self.get_response("describe_help"), [""]


	def handle_hint(self, command, player, arg):
		template = self.data.get_hint(arg)

		if not template:
			template = self.data.get_hint("default")

		return True, template, [arg]


	def handle_ignore(self, command, player, arg):
		return True, "", []


	def handle_immune(self, command, player, arg):
		template = ""

		player.immune = arg
		if arg:
			template = self.get_response("confirm_immune_on")
		else:
			template = self.get_response("confirm_immune_off")

		return True, template, [arg]


	def handle_insert(self, command, player, item, proposed_container):

		template = ""
		content = [item, proposed_container]

		if not proposed_container.is_container():
			return False, self.get_response("reject_not_container"), content

		if item is proposed_container:
			return False, self.get_response("reject_container_self"), content

		if proposed_container in item.containers:
			return False, self.get_response("reject_already_contained"), content

		if not item.is_portable():
			return False, self.get_response("reject_not_portable"), content

		if item.is_liquid() and not proposed_container.is_liquid_container():
			return False, self.get_response("reject_insert_liquid"), content

		if not item.is_liquid() and proposed_container.is_liquid_container():
			return False, self.get_response("reject_insert_solid"), content

		if proposed_container.has_items():
			return False, self.get_response("reject_not_empty"), content

		if not proposed_container.can_accommodate(item):
			return False, self.get_response("reject_container_size"), content

		if not item.is_copyable():
			item.remove_from_containers()
		proposed_container.insert(item)

		return True, self.get_response("confirm_inserted"), content


	def handle_inventory(self, command, player):
		if not player.holding_items():
			return True, self.get_response("list_inventory_empty"), [""]
		return True, self.get_response("list_inventory_nonempty"), [player.describe_inventory()]


	def handle_locate(self, command, player, item):
		template = self.get_response("describe_locate_primary")
		primary_containers = item.containers
		primary_container_descriptions = [str(container.data_id) + ":" + container.longname for container in primary_containers]
		contents = [item.shortname, str(primary_container_descriptions)]

		item_copies = item.copied_to
		copy_container_descriptions = []
		for item_copy in item_copies:
			copy_container = item_copy.get_first_container()
			copy_container_descriptions.append(str(copy_container.data_id) + ":" + copy_container.longname)

		if copy_container_descriptions:
			template += self.get_response("describe_locate_copies")
			contents.append(str(copy_container_descriptions))

		return True, template, contents


	def handle_look(self, command, player):
		template = self.get_response("describe_location")

		if player.has_non_silent_items_nearby():
			template += self.get_response("list_location")

		return True, template, player.get_full_location_description()


	def handle_node(self, command, player, arg=None):
		if not arg:
			return True, self.get_response("describe_node"), [player.location.data_id]

		location_id = player.location.data_id
		try:
			location_id = int(arg)
			proposed_location = self.data.get_location(location_id)
			if proposed_location:
				template, content = self.execute_go(player, arg, proposed_location)
				return True, template, content
		except:
			pass

		return False, self.get_response("reject_no_node"), [arg]


	def handle_pick(self, command, player, item):
		return self.handle_take(command, player, item)


	def handle_pour(self, command, player, item, destination):
		if not item.is_liquid():
			return False, self.get_response("reject_not_liquid"), [item]

		item_source = item.get_first_container()
		item.destroy()
		content = [item, item_source, destination]
		return True, self.get_response("confirm_poured_with_destination"), content


	def handle_quit(self, command, player):
		player.decrement_instructions()
		player.playing = False
		return True, self.get_response("confirm_quit"), [""]


	def handle_read(self, command, player, item):
		if not item.writing:
			return False, self.get_response("reject_no_writing"), [item]
		return True, self.get_response("describe_writing"), [item.writing]


	def handle_say(self, command, player, word):
		return True, self.get_response("confirm_say"), [word]


	def handle_score(self, command, player):
		player.decrement_instructions()
		return True, self.get_response("describe_score"), [player.score, player.instructions]


	def handle_set(self, command, player, item):
		return self.handle_drop(command, player, item)


	def handle_switch(self, command, player, item, transition):
		template = self.get_response("describe_switch_item")

		if transition == SwitchTransition.OFF:
			if not item.is_on():
				return False, self.get_response("reject_already_switched"), [item, item.get_state_text()]
			item.switch_off()

		elif transition == SwitchTransition.ON:
			if item.is_on():
				return False, self.get_response("reject_already_switched"), [item, item.get_state_text()]
			item.switch_on()

		elif transition == SwitchTransition.TOGGLE:
			item.switch_toggle()

		return True, template, [item, item.get_state_text()]


	def handle_take(self, command, player, item, proposed_container=None):

		owner = item.get_sentient_owner()
		if owner:
			return False, self.get_response("reject_take_animate"), [item, owner]

		if proposed_container:
			return self.handle_insert(command, player, item, proposed_container)

		content = [item]
		if not item.is_portable():
			return False, self.get_response("reject_not_portable"), content

		if item.is_liquid():
			return False, self.get_response("reject_take_liquid"), content

		if not player.can_carry(item):
			return False, self.get_response("reject_too_full"), content

		player.take_item(item)
		return True, self.get_response("confirm_taken"), content


	def handle_teleport(self, command, player, destination):
		template, content = self.execute_go(player, None, destination)
		self.interact_vision(player, None, self.execute_see_location)
		return True, template, content


	def handle_toggle(self, command, player, item):
		if not item.is_switchable():
			return False, self.get_response("reject_no_know_how"), [item]
		return self.handle_switch(command, player, item, SwitchTransition.TOGGLE)


	def handle_verbose(self, command, player, arg):
		template = ""

		player.verbose = arg
		if arg:
			template = self.get_response("confirm_verbose_on")
		else:
			template = self.get_response("confirm_verbose_off")

		return True, template, [arg]


	def handle_wear(self, command, player, item):
		content = [item]

		if not item.is_wearable():
			return False, self.get_response("reject_not_wearable"), content

		if item.being_worn:
			return False, self.get_response("reject_already_wearing"), content

		player.take_item(item)
		item.being_worn = True
		return True, self.get_response("confirm_wearing"), content


	def interact_vision(self, player, arg, interaction):

		if player.has_light_and_needs_no_light():
			return self.get_response("reject_excess_light"), [""]

		elif not player.has_light():
			return self.get_response("reject_no_light"), [""]

		return interaction(player, arg)
