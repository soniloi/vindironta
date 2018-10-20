from adventure.command_collection import CommandCollection
from adventure.input_collection import InputCollection
from adventure.item_collection import ItemCollection
from adventure.location_collection import LocationCollection
from adventure.text_collection import TextCollection

class DataCollection:

	def __init__(self, reader, resolvers):
		self.commands = CommandCollection(reader, resolvers)
		self.locations = LocationCollection(reader)
		self.items = ItemCollection(reader, self.locations.locations.copy())
		self.hints = TextCollection(reader)
		self.explanations = TextCollection(reader)
		self.responses = TextCollection(reader)
		self.puzzles = TextCollection(reader)
		self.events = TextCollection(reader)
		self.inputs = InputCollection(reader)


	def list_commands(self):
		return self.commands.list_commands()


	def get_location(self, location_id):
		return self.locations.get(location_id)


	def get_item(self, item_shortname):
		return self.items.get(item_shortname)


	def get_hint(self, hint_key):
		return self.hints.get(hint_key)


	def get_explanation(self, explanation_key):
		return self.explanations.get(explanation_key)


	def get_response(self, response_key):
		return self.responses.get(response_key)


	def matches_input(self, internal_key, input_key):
		return self.inputs.matches(internal_key, input_key)
