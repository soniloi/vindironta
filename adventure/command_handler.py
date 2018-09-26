from adventure.direction import Direction

class CommandHandler:

	DIRECTIONS = {
		5 : Direction.BACK,
		13 : Direction.DOWN,
		16 : Direction.EAST,
		34 : Direction.NORTH,
		35 : Direction.NORTHEAST,
		36 : Direction.NORTHWEST,
		52 : Direction.SOUTH,
		53 : Direction.SOUTHEAST,
		54 : Direction.SOUTHWEST,
		60 : Direction.UP,
		62 : Direction.WEST,
	}

	def init_data(self, data):
		self.data = data


	def get_command_function(self, command_function_name):
		return getattr(self, command_function_name, None)


	def get_response(self, response_key):
		return self.data.responses.get(response_key)


	def handle_drop(self, player, arg):
		#TODO: handle None arg

		template = ""
		content = ""

		item = self.data.items.get(arg)
		if not item:
			template = self.get_response("reject_unknown")

		else:
			content = item.shortname
			if not player.is_carrying(item):
				template = self.get_response("reject_not_holding")
			else:
				player.inventory.remove(item)
				player.location.insert(item)
				template = self.get_response("confirm_dropped")

		return template, content


	def handle_go(self, player, arg):
		direction = CommandHandler.DIRECTIONS[arg]

		proposed_location, template = self.get_proposed_location_and_reject_template(player, direction)
		content = ""

		if proposed_location:
			player.previous_location = player.location
			player.location = proposed_location
			template = self.get_response("confirm_look")
			content = proposed_location.get_full_description()

		return template, content


	def get_proposed_location_and_reject_template(self, player, direction):

		if direction == Direction.BACK:
			proposed_location = player.previous_location
			reject_template = self.get_response("reject_no_back")

		else:
			proposed_location = player.location.get_adjacent_location(direction)
			reject_template = self.get_response("reject_no_direction")

		return proposed_location, reject_template


	def handle_inventory(self, player, arg):

		template = ""
		content = ""

		if not player.holding_items():
			template = template = self.get_response("list_inventory_empty")
		else:
			template = template = self.get_response("list_inventory_nonempty")
			content = player.inventory.get_contents_description()

		return template, content


	def handle_look(self, player, arg):

		template = self.get_response("describe_location")

		if player.has_items_nearby():
			template += self.get_response("list_location")

		return template, player.location.get_full_description()


	def handle_quit(self, player, arg):
		player.playing = False
		return self.get_response("confirm_quit"), ""


	def handle_score(self, player, arg):
		return self.get_response("describe_score"), player.score


	def handle_take(self, player, arg):
		#TODO: handle None arg

		template = ""
		content = ""

		item = self.data.items.get(arg)
		if not item:
			template = self.get_response("reject_unknown")

		else:
			content = item.shortname
			if player.is_carrying(item):
				template = self.get_response("reject_already")

			elif not player.location.contains(item):
				template = self.get_response("reject_not_here")
			else:
				item.container.remove(item)
				player.inventory.insert(item)
				template = self.get_response("confirm_taken")

		return template, content
