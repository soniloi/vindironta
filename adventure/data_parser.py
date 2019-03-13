from adventure.command_parser import CommandParser
from adventure.data_collection import DataCollection
from adventure.event_parser import EventParser
from adventure.input_parser import InputParser
from adventure.inventory_parser import InventoryParser
from adventure.item_parser import ItemParser
from adventure.location_parser import LocationParser
from adventure.player_parser import PlayerParser
from adventure.text_parser import TextParser

class DataParser:

	def parse(self, content_input, resolvers):
		commands = CommandParser().parse(content_input["commands"], resolvers)
		inventories = InventoryParser().parse(content_input["inventories"])
		locations = LocationParser().parse(content_input["locations"])
		elements_by_id = locations.locations.copy()
		commands_by_id = commands.commands_by_id.copy()
		items = ItemParser().parse(content_input["items"], elements_by_id, commands_by_id)
		hints = TextParser().parse(content_input["hints"])
		explanations = TextParser().parse(content_input["explanations"])
		responses = TextParser().parse(content_input["responses"])
		inputs = InputParser().parse(content_input["inputs"])
		events = EventParser().parse(
			content_input["events"],
			commands.commands_by_id.copy(),
			items.items_by_id.copy(),
			locations.locations.copy(),
		)

		data = DataCollection(
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

		player = PlayerParser().parse(
			content_input["players"],
			locations.locations.copy(),
			inventories.get_default(),
			inventories.get_all(),
		)

		return data, player
