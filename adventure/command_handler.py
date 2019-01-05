from adventure.item import SwitchTransition
from adventure.resolver import Resolver

class CommandHandler(Resolver):

	def handle_climb(self, command, player, arg=None):
		return False, self.get_response("reject_climb"), [], []


	def handle_commands(self, command, player):
		template = self.get_response("describe_commands")
		content = [self.data.list_commands()]
		return True, template, content, []


	def handle_consume(self, command, player, item):
		content_args = [item]

		if not item.is_edible():
			return False, self.get_response("reject_not_consumable"), content_args, []

		item.destroy()
		return True, self.get_response("confirm_consume"), content_args, [item]


	def handle_describe(self, command, player, item):
		template = self.get_response("describe_item")
		if item.is_switchable():
			template += self.get_response("describe_item_switch")
		return True, template, item.get_full_description(), [item]


	def handle_drink(self, command, player, item):
		if not item.is_liquid():
			return False, self.get_response("reject_drink_solid"), [item], []

		return self.handle_consume(command, player, item)


	def handle_drop(self, command, player, item):
		content_args = [item]
		next_args = [item]

		if item.is_liquid():
			content_args.append(item.get_first_container())
			item.destroy()
			return True, self.get_response("confirm_poured_no_destination"), content_args, next_args

		player.drop_item(item)
		return True, self.get_response("confirm_dropped"), content_args, next_args


	def handle_eat(self, command, player, item):
		if item.is_liquid():
			return False, self.get_response("reject_eat_liquid"), [item], []

		return self.handle_consume(command, player, item)


	def handle_empty(self, command, player, item):
		content_args = [item]
		next_args = [item]

		if not item.is_container():
			return False, self.get_response("reject_not_container"), content_args, []

		if not item.has_items():
			return False, self.get_response("reject_already_empty"), content_args, []

		contained_item = item.get_contained_item()
		content_args.append(contained_item)
		item.remove(contained_item)

		if item.is_liquid_container():
			contained_item.destroy()
			return True, self.get_response("confirm_emptied_liquid"), content_args, next_args

		outermost_item = item.get_outermost_container()
		outermost_item.insert(contained_item)
		return True, self.get_response("confirm_emptied_solid"), content_args, next_args


	def handle_explain(self, command, player, arg):
		template = self.data.get_explanation(arg)

		if not template:
			template = self.data.get_explanation("default")

		return True, template, [arg], [arg]


	def handle_feed(self, command, player, proposed_gift, proposed_recipient):
		content_args = [proposed_gift, proposed_recipient]

		if not proposed_recipient.is_sentient():
			return False, self.get_response("reject_give_inanimate"), content_args, []

		if not proposed_gift.is_edible():
			return False, self.get_response("reject_not_consumable"), content_args, []

		proposed_gift.destroy()
		return True, self.get_response("confirm_feed"), content_args, [proposed_gift, proposed_recipient]


	def handle_give(self, command, player, proposed_gift, proposed_recipient):
		content_args = [proposed_gift, proposed_recipient]

		if not proposed_recipient.is_sentient():
			return False, self.get_response("reject_give_inanimate"), content_args, []

		if proposed_gift.is_liquid():
			return False, self.get_response("reject_give_liquid"), content_args, []

		proposed_gift.remove_from_containers()
		proposed_recipient.insert(proposed_gift)
		return True, self.get_response("confirm_given"), content_args, [proposed_gift, proposed_recipient]


	def handle_go(self, command, player, proposed_location):
		obstructions = player.get_obstructions()
		if obstructions and proposed_location is not player.get_previous_location():
			template_key, content = self.reject_go_obstructed(player, obstructions)
			return False, self.get_response(template_key), content, []

		if not player.has_light() and not proposed_location.gives_light() and not player.is_immune():
			self.kill_player(player)
			template = self.get_response("death_darkness")
			return True, template, [], [proposed_location]

		self.update_previous_location(player, proposed_location)
		template, content = self.execute_go(player, proposed_location)
		self.interact_vision(player, None, self.execute_see_location)
		return True, template, content, [proposed_location]


	def kill_player(self, player):
		player.set_alive(False)
		player.drop_all_items()


	def reject_go_obstructed(self, player, obstructions):
		if player.has_light():
			return "reject_obstruction_known", [obstructions[0].longname]
		return "reject_obstruction_unknown", []


	def update_previous_location(self, player, proposed_location):
		if proposed_location.can_reach(player.location):
			player.set_previous_location(player.location)
		else:
			player.set_previous_location(None)


	def execute_go(self, player, proposed_location):
		player.location = proposed_location
		return self.interact_vision(player, None, self.complete_go)


	def complete_go(self, player, arg):
		template = self.get_response("confirm_look")
		if player.has_non_silent_items_nearby():
			template += self.get_response("list_location")

		return template, player.get_arrival_location_description()


	def execute_see_location(self, player, arg):
		player.see_location()


	def handle_go_disambiguate(self, command, player, arg):
		return False, self.get_response("reject_go"), [], []


	def handle_help(self, command, player, arg):
		player.decrement_instructions()
		return True, self.get_response("describe_help"), [], []


	def handle_hint(self, command, player, arg):
		template = self.data.get_hint(arg)

		if not template:
			template = self.data.get_hint("default")

		return True, template, [arg], [arg]


	def handle_ignore(self, command, player, arg):
		return True, "", [], []


	def handle_immune(self, command, player, arg):
		template = ""

		player.set_immune(arg)
		if arg:
			template = self.get_response("confirm_immune_on")
		else:
			template = self.get_response("confirm_immune_off")

		return True, template, [arg], [arg]


	def handle_insert(self, command, player, item, proposed_container):
		template = ""
		content_args = [item, proposed_container]

		if not proposed_container.is_container():
			return False, self.get_response("reject_not_container"), content_args, []

		if item is proposed_container:
			return False, self.get_response("reject_container_self"), content_args, []

		if proposed_container in item.containers:
			return False, self.get_response("reject_already_contained"), content_args, []

		if not item.is_portable():
			return False, self.get_response("reject_not_portable"), content_args, []

		if item.is_liquid() and not proposed_container.is_liquid_container():
			return False, self.get_response("reject_insert_liquid"), content_args, []

		if not item.is_liquid() and proposed_container.is_liquid_container():
			return False, self.get_response("reject_insert_solid"), content_args, []

		if proposed_container.has_items():
			return False, self.get_response("reject_not_empty"), content_args, []

		if not proposed_container.can_accommodate(item):
			return False, self.get_response("reject_container_size"), content_args, []

		if not item.is_copyable():
			item.remove_from_containers()
		proposed_container.insert(item)

		return True, self.get_response("confirm_inserted"), content_args, [item, proposed_container]


	def handle_inventory(self, command, player):
		if not player.holding_items():
			return True, self.get_response("list_inventory_empty"), [""], []
		return True, self.get_response("list_inventory_nonempty"), [player.describe_inventory()], []


	def handle_locate(self, command, player, item):
		template = self.get_response("describe_locate_primary")
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
			template += self.get_response("describe_locate_copies")
			content_args.append(str(copy_container_descriptions))

		return True, template, content_args, next_args


	def handle_look(self, command, player):
		template = self.get_response("describe_location")

		if player.has_non_silent_items_nearby():
			template += self.get_response("list_location")

		return True, template, player.get_full_location_description(), []


	def handle_node(self, command, player, arg=None):
		if not arg:
			return True, self.get_response("describe_node"), [player.location.data_id], []

		location_id = player.location.data_id
		try:
			location_id = int(arg)
			proposed_location = self.data.get_location(location_id)
			if proposed_location:
				template, content = self.execute_go(player, proposed_location)
				return True, template, content, [location_id]
		except:
			pass

		return False, self.get_response("reject_no_node"), [arg], []


	def handle_pick(self, command, player, item):
		return self.handle_take(command, player, item)


	def handle_pour(self, command, player, item, destination):
		content_args = [item]
		next_args = [item, destination]

		if not item.is_liquid():
			return False, self.get_response("reject_not_liquid"), content_args, []

		source = item.get_first_container()
		item.destroy()
		content_args.extend([destination, source])

		return True, self.get_response("confirm_poured_with_destination"), content_args, next_args


	def handle_quit(self, command, player):
		player.decrement_instructions()
		player.set_playing(False)
		return True, self.get_response("confirm_quit"), [], []


	def handle_read(self, command, player, item):
		if not item.writing:
			return False, self.get_response("reject_no_writing"), [item], []
		return True, self.get_response("describe_writing"), [item.writing], [item]


	def handle_rub(self, command, player, item):
		return True, "", [], [item]


	def handle_say(self, command, player, word):
		return True, self.get_response("confirm_say"), [word], [word]


	def handle_score(self, command, player):
		player.decrement_instructions()
		return True, self.get_response("describe_score"), [player.score, player.instructions], []


	def handle_set(self, command, player, item):
		return self.handle_drop(command, player, item)


	def handle_switch(self, command, player, item, transition):
		template = self.get_response("describe_switch_item")

		if transition == SwitchTransition.OFF:
			if not item.is_on():
				return False, self.get_response("reject_already_switched"), [item, item.get_state_text()], []
			item.switch_off()

		elif transition == SwitchTransition.ON:
			if item.is_on():
				return False, self.get_response("reject_already_switched"), [item, item.get_state_text()], []
			item.switch_on()

		elif transition == SwitchTransition.TOGGLE:
			item.switch_toggle()

		return True, template, [item, item.get_state_text()], [item, transition]


	def handle_take(self, command, player, item, proposed_container=None):
		content_args = [item]

		owner = item.get_sentient_owner()
		if owner:
			content_args.append(owner)
			return False, self.get_response("reject_take_animate"), content_args, []

		if proposed_container:
			return self.handle_insert(command, player, item, proposed_container)

		if not item.is_portable():
			return False, self.get_response("reject_not_portable"), content_args, []

		if item.is_liquid():
			return False, self.get_response("reject_take_liquid"), content_args, []

		if not player.can_carry(item):
			return False, self.get_response("reject_too_full"), content_args, []

		player.take_item(item)
		next_args = [item]
		if proposed_container:
			next_args.append(proposed_container)

		return True, self.get_response("confirm_taken"), content_args, next_args


	def handle_teleport(self, command, player, destination):
		template, content = self.execute_go(player, destination)
		self.interact_vision(player, None, self.execute_see_location)
		return True, template, content, [destination]


	def handle_toggle(self, command, player, item):
		if not item.is_switchable():
			return False, self.get_response("reject_no_know_how"), [item], []
		return self.handle_switch(command, player, item, SwitchTransition.TOGGLE)


	def handle_verbose(self, command, player, arg):
		template = ""

		player.set_verbose(arg)
		if arg:
			template = self.get_response("confirm_verbose_on")
		else:
			template = self.get_response("confirm_verbose_off")

		return True, template, [arg], [arg]


	def handle_wear(self, command, player, item):
		if not item.is_wearable():
			return False, self.get_response("reject_not_wearable"), [item], []

		if item.being_worn:
			return False, self.get_response("reject_already_wearing"), [item], []

		player.take_item(item)
		item.being_worn = True
		return True, self.get_response("confirm_wearing"), [item], [item]


	def interact_vision(self, player, arg, interaction):

		if player.has_light_and_needs_no_light():
			return self.get_response("reject_excess_light"), []

		elif not player.has_light():
			return self.get_response("reject_no_light"), []

		return interaction(player, arg)
