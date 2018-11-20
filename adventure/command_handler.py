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


	def handle_climb(self, player, arg=None):
		return self.get_response("reject_climb"), [""]


	def handle_commands(self, player):
		template = self.get_response("describe_commands")
		content = [self.data.list_commands()]
		return template, content


	def handle_describe(self, player, item):
		template = self.get_response("describe_item")
		if item.is_switchable():
			template += self.get_response("describe_item_switch")
		return template, item.get_full_description()


	def handle_drop(self, player, item):

		if item.is_liquid():
			player.lose_item(item)
			return self.get_response("confirm_poured"), [item.shortname, item.container.shortname]

		player.drop_item(item)
		return self.get_response("confirm_dropped"), [item.shortname]


	def handle_empty(self, player, item):
		content = [item.shortname]
		if not item.is_container():
			return self.get_response("reject_not_container"), content

		if not item.has_items():
			return self.get_response("reject_already_empty"), content

		contained_item = item.get_contained_item()
		content.append(contained_item.shortname)
		item.remove(contained_item)

		if item.is_liquid_container():
			return self.get_response("confirm_emptied_liquid"), content

		outermost_item = item.get_outermost_container()
		outermost_item.insert(contained_item)
		return self.get_response("confirm_emptied_solid"), content


	def handle_explain(self, player, arg):
		template = self.data.get_explanation(arg)

		if not template:
			template = self.data.get_explanation("default")

		return template, [arg]


	def handle_give(self, player, proposed_gift, proposed_recipient):

		content = [proposed_gift.shortname, proposed_recipient.shortname]

		if not proposed_recipient.is_sentient():
			return self.get_response("reject_give_inanimate"), content

		if proposed_gift.is_liquid():
			return self.get_response("reject_give_liquid"), content

		proposed_gift.container.remove(proposed_gift)
		proposed_recipient.insert(proposed_gift)
		return self.get_response("confirm_given"), content


	def handle_go(self, player, arg):
		direction = CommandHandler.DIRECTIONS[arg]

		proposed_location, reject_template_key = self.get_proposed_location_and_reject_key(player, direction)
		template = self.get_response(reject_template_key)
		content = [""]

		if proposed_location:
			template, content = self.execute_go_if_not_obstructed(player, arg, proposed_location)

		return template, content


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


	def handle_go_disambiguate(self, player, arg):
		return self.get_response("reject_go"), [""]


	def handle_help(self, player, arg):
		player.decrement_instructions()
		return self.get_response("describe_help"), [""]


	def handle_hint(self, player, arg):
		template = self.data.get_hint(arg)

		if not template:
			template = self.data.get_hint("default")

		return template, [arg]


	def handle_ignore(self, player, arg):
		return "", ""


	def handle_immune(self, player, arg):
		template = ""

		player.immune = arg
		if arg:
			template = self.get_response("confirm_immune_on")
		else:
			template = self.get_response("confirm_immune_off")

		return template, [""]


	def handle_insert(self, player, item, proposed_container):

		template = ""
		content = [item.shortname, proposed_container.shortname]

		if not proposed_container.is_container():
			return self.get_response("reject_not_container"), content

		if item is proposed_container:
			return self.get_response("reject_container_self"), content

		if item.container is proposed_container:
			return self.get_response("reject_already_contained"), content

		if not item.is_portable():
			return self.get_response("reject_not_portable"), content

		if item.is_liquid() and not proposed_container.is_liquid_container():
			return self.get_response("reject_insert_liquid"), content

		if not item.is_liquid() and proposed_container.is_liquid_container():
			return self.get_response("reject_insert_solid"), content

		if proposed_container.has_items():
			return self.get_response("reject_not_empty"), content

		if not proposed_container.can_accommodate(item):
			return self.get_response("reject_container_size"), content

		item.container.remove(item)
		proposed_container.insert(item)
		return self.get_response("confirm_inserted"), content


	def handle_inventory(self, player):
		if not player.holding_items():
			return self.get_response("list_inventory_empty"), [""]
		return self.get_response("list_inventory_nonempty"), [player.describe_inventory()]


	def handle_locate(self, player, item):
		template = self.get_response("describe_locate")
		container = item.container
		# TODO: fix
		longname = "inventory"
		if not isinstance(container, Inventory):
			longname = container.longname
		contents = [item.shortname, container.data_id, longname]
		return template, contents


	def handle_look(self, player):
		template = self.get_response("describe_location")

		if player.has_non_silent_items_nearby():
			template += self.get_response("list_location")

		return template, player.get_full_location_description()


	def handle_node(self, player, arg=None):

		template = ""
		content = [""]

		if not arg:
			template = self.get_response("describe_node")
			content = [player.location.data_id]
		else:
			template = self.get_response("reject_no_node")
			location_id = player.location.data_id
			try:
				location_id = int(arg)
				proposed_location = self.data.get_location(location_id)
				if proposed_location:
					template, content = self.execute_go(player, arg, proposed_location)
			except:
				pass

		return template, content


	def handle_pick(self, player, item):
		return self.handle_take(player, item)


	def handle_pour(self, player, item):
		if not item.is_liquid():
			return self.get_response("reject_not_liquid"), [item.shortname]
		return self.handle_drop(player, item)


	def handle_quit(self, player):
		player.decrement_instructions()
		player.playing = False
		return self.get_response("confirm_quit"), [""]


	def handle_read(self, player, item):
		if not item.writing:
			return self.get_response("reject_no_writing"), [item.shortname]
		return self.get_response("describe_writing"), [item.writing]


	def handle_score(self, player):
		player.decrement_instructions()
		return self.get_response("describe_score"), [player.score, player.instructions]


	def handle_set(self, player, item):
		return self.handle_drop(player, item)


	def handle_switch(self, player, item, transition):
		template = self.get_response("describe_switch_item")

		if transition == SwitchTransition.OFF:
			if not item.is_on():
				template = self.get_response("reject_already_switched")
			item.switch_off()

		elif transition == SwitchTransition.ON:
			if item.is_on():
				template = self.get_response("reject_already_switched")
			item.switch_on()

		elif transition == SwitchTransition.TOGGLE:
			item.switch_toggle()

		return template, [item.shortname, item.get_state_text()]


	def handle_take(self, player, item, proposed_container=None):

		owner = item.get_sentient_owner()
		if owner:
			return self.get_response("reject_take_animate"), [item.shortname, owner.shortname]

		if proposed_container:
			return self.handle_insert(player, item, proposed_container)

		template = ""
		if not item.is_portable():
			template = self.get_response("reject_not_portable")

		elif item.is_liquid():
			template = self.get_response("reject_take_liquid")

		elif not player.can_carry(item):
			template = self.get_response("reject_too_full")

		else:
			player.take_item(item)
			template = self.get_response("confirm_taken")

		return template, [item.shortname]


	def handle_toggle(self, player, item):
		if not item.is_switchable():
			return self.get_response("reject_no_know_how"), [item.shortname]
		return self.handle_switch(player, item, SwitchTransition.TOGGLE)


	def handle_verbose(self, player, arg):
		template = ""

		player.verbose = arg
		if arg:
			template = self.get_response("confirm_verbose_on")
		else:
			template = self.get_response("confirm_verbose_off")

		return template, [""]


	def handle_wear(self, player, item):
		template = ""

		if not item.is_wearable():
			template = self.get_response("reject_not_wearable")

		elif item.being_worn:
			template = self.get_response("reject_already_wearing")

		else:
			player.take_item(item)
			item.being_worn = True
			template = self.get_response("confirm_wearing")

		return template, [item.shortname]


	def interact_vision(self, player, arg, interaction):

		if player.has_light_and_needs_no_light():
			return self.get_response("reject_excess_light"), [""]

		elif not player.has_light():
			return self.get_response("reject_no_light"), [""]

		return interaction(player, arg)
