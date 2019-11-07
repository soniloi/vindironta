class DataCollection:

	def __init__(self, commands, inventories, locations, elements_by_id, items, item_related_commands, hints, explanations,
			responses, inputs, events):
		self.commands = commands
		self.inventories = inventories
		self.locations = locations
		self.elements_by_id = elements_by_id
		self.items = items
		self.item_related_commands = item_related_commands
		self.hints = hints
		self.explanations = explanations
		self.responses = responses
		self.inputs = inputs
		self.events = events


	def get_commands(self):
		return self.commands


	def list_commands(self):
		return self.commands.list_commands()


	def get_smash_command_id(self):
		return self.commands.get_smash_command_id()


	def get_item_related_commands(self):
		return self.item_related_commands


	def get_element_by_id(self, data_id):
		return self.elements_by_id.get(data_id)


	def get_location(self, location_id):
		return self.locations.get(location_id)


	def get_item_list_by_name(self, item_shortname):
		return self.items.get_list_by_name(item_shortname)


	def get_item_by_id(self, item_id):
		return self.items.get_by_id(item_id)


	def get_hint(self, hint_key):
		return self.hints.get(hint_key)


	def get_explanation(self, explanation_key):
		return self.explanations.get(explanation_key)


	def get_response(self, response_key):
		return self.responses.get(response_key)


	def get_start_message(self):
		return self.responses.get("describe_start")


	def matches_input(self, internal_key, input_key):
		return self.inputs.matches(internal_key, input_key)


	def get_events(self, event_key):
		return self.events.get(event_key)


	def get_puzzle_count(self):
		return self.events.puzzle_count


	def get_collectible_count(self):
		return self.items.collectible_count
