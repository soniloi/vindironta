class DataCollection:

	def __init__(self, commands, inventories, locations, elements_by_id, items, hints, explanations, responses,
			inputs, events):
		self.commands = commands
		self.inventories = inventories
		self.locations = locations
		self.elements_by_id = elements_by_id
		self.items = items
		self.hints = hints
		self.explanations = explanations
		self.responses = responses
		self.inputs = inputs
		self.events = events


	def get_commands(self):
		return self.commands


	def list_commands(self):
		return self.commands.list_commands()


	def get_element_by_id(self, data_id):
		return self.elements_by_id.get(data_id)


	def get_inventory_template(self, inventory_id):
		return self.inventories.get(inventory_id)


	def get_default_inventory_template(self):
		return self.inventories.get_default()


	def get_inventory_templates(self):
		return self.inventories.get_all()


	def get_location(self, location_id):
		return self.locations.get(location_id)


	def get_item(self, item_shortname):
		return self.items.get(item_shortname)


	def get_item_by_id(self, item_id):
		return self.items.get_by_id(item_id)


	def get_hint(self, hint_key):
		return self.hints.get(hint_key)


	def get_explanation(self, explanation_key):
		return self.explanations.get(explanation_key)


	def get_response(self, response_key):
		return self.responses.get(response_key)


	def matches_input(self, internal_key, input_key):
		return self.inputs.matches(internal_key, input_key)


	def get_event(self, event_key):
		return self.events.get(event_key)
