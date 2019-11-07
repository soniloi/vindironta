import json

from adventure.argument_resolver import ArgumentResolver
from adventure.command_handler import CommandHandler
from adventure.command_parser import CommandParser
from adventure.data_collection import DataCollection
from adventure.event_parser import EventParser
from adventure.event_resolver import EventResolver
from adventure.file_reader import FileReader
from adventure.game import Game
from adventure.input_parser import InputParser
from adventure.inventory_parser import InventoryParser
from adventure.item_parser import ItemParser
from adventure.life_resolver import LifeResolver
from adventure.location_parser import LocationParser
from adventure.player import Player
from adventure.player_parser import PlayerParser
from adventure.post_parse_validator import PostParseValidator
from adventure.resolvers import Resolvers
from adventure.text_parser import TextParser
from adventure.vision_resolver import VisionResolver

class DataParser:

	VALIDATION_MESSAGE_FILENAME = "validation.txt"

	def parse(self, filename, text_input=False):
		content = None
		if text_input:
			content = self.get_content_text(filename)
		else:
			content = self.get_content_binary(filename)
		json_content = json.loads(content)
		return self.parse_file(json_content)


	def get_content_text(self, filename):
		with open(filename, "r") as input_file:
			return input_file.read()


	def get_content_binary(self, filename):
		with open(filename, "rb") as input_file:
			reader = FileReader(input_file)
			return reader.get_content()


	def parse_file(self, json_content):
		resolvers = self.init_resolvers()

		data, player, validation = self.parse_content(json_content, resolvers)
		if validation:
			with open(DataParser.VALIDATION_MESSAGE_FILENAME, "w") as validation_file:
				for validation_line in validation:
					validation_file.write(validation_line.get_formatted_message() + "\n")
			print("Validation errors found, see {0}.".format(DataParser.VALIDATION_MESSAGE_FILENAME))

		resolvers.argument_resolver.init_data(data)
		resolvers.command_handler.init_data(data)
		resolvers.vision_resolver.init_data(data)
		resolvers.event_resolver.init_data(data)
		resolvers.life_resolver.init_data(data)

		return Game(data, player)


	def init_resolvers(self):
		argument_resolver = ArgumentResolver()
		command_handler = CommandHandler()
		vision_resolver = VisionResolver()
		event_resolver = EventResolver()
		life_resolver = LifeResolver()
		return Resolvers(
			vision_resolver=vision_resolver,
			argument_resolver=argument_resolver,
			command_handler=command_handler,
			event_resolver=event_resolver,
			life_resolver=life_resolver,
		)


	def parse_content(self, content_input, resolvers):
		commands, teleport_infos, command_validation = CommandParser().parse(content_input["commands"], resolvers)
		inventories, inventory_validation = InventoryParser().parse(content_input["inventories"])
		locations, location_validation = LocationParser().parse(content_input["locations"], teleport_infos)
		elements_by_id = locations.locations.copy()
		commands_by_id = commands.commands_by_id.copy()
		items, related_commands, item_validation = ItemParser().parse(content_input["items"], elements_by_id, commands_by_id)
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
			item_related_commands=related_commands,
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

		parse_validation = command_validation + location_validation + inventory_validation + item_validation
		post_parse_validation = PostParseValidator().validate(data)
		validation = parse_validation + post_parse_validation

		return data, player, validation
