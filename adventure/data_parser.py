from adventure.command_parser import CommandParser
from adventure.data_collection import DataCollection
from adventure.event_collection import EventCollection
from adventure.input_collection import InputCollection
from adventure.inventory_parser import InventoryParser
from adventure.item_collection import ItemCollection
from adventure.location_parser import LocationParser
from adventure.text_collection import TextCollection

class DataParser:

	def parse(self, content_input, resolvers):
		commands = CommandParser().parse(content_input["commands"], resolvers)
		inventories = InventoryParser().parse(content_input["inventories"])
		locations = LocationParser().parse(content_input["locations"])

		elements_by_id = locations.locations.copy()
		items = ItemCollection(content_input["items"], elements_by_id)
		hints = TextCollection(content_input["hints"])
		explanations = TextCollection(content_input["explanations"])
		responses = TextCollection(content_input["responses"])
		inputs = InputCollection(content_input["inputs"])
		events = EventCollection(
			content_input["events"],
			commands.commands_by_id.copy(),
			items.items_by_id.copy(),
			locations.locations.copy(),
		)

		return DataCollection(
			commands=commands,
			inventories=inventories,
			locations=locations,
			elements_by_id=elements_by_id,
			items=items,
			hints=hints,
			explanations=explanations,
			responses=responses,
			inputs=inputs,
			events=events,
		)
