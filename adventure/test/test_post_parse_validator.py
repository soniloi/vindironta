import unittest

from adventure.command import Command
from adventure.command_collection import CommandCollection
from adventure.data_collection import DataCollection
from adventure.direction import Direction
from adventure.element import Labels
from adventure.inventory import Inventory
from adventure.inventory_collection import InventoryCollection
from adventure.item import Item, ListTemplateType, SwitchableItem, SwitchInfo, UsableItem
from adventure.item_collection import ItemCollection
from adventure.location import Location
from adventure.location_collection import LocationCollection
from adventure.post_parse_validator import PostParseValidator
from adventure.validation import Severity

class TestPostParseValidator(unittest.TestCase):

	def setUp(self):
		self.setup_commands()
		self.setup_inventories()
		self.setup_locations()
		self.setup_items()
		self.data_collection = DataCollection(
			commands=self.command_collection,
			inventories=self.inventory_collection,
			locations=self.location_collection,
			elements_by_id=None,
			items=self.item_collection,
			item_related_commands=None,
			hints=None,
			explanations=None,
			responses=None,
			inputs=None,
			events=None,
		)
		self.validator = PostParseValidator()


	def setup_commands(self):
		self.commands_by_id = {}
		self.commands_by_id[56] = Command(56, 0x0, [], [], ["take", "t"],  {})
		self.command_collection = CommandCollection({}, self.commands_by_id, "command_list")


	def setup_inventories(self):
		self.inventories_by_id = {}
		self.inventories_by_id[0] = Inventory(0, 0x1, Labels("Main Inventory", "in the main inventory", ", where items live usually."), 3)
		self.inventory_collection = InventoryCollection(self.inventories_by_id)


	def setup_locations(self):
		self.lighthouse_location = Location(12, 0x603, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.locations_by_id = {}
		self.locations_by_id[12] = self.lighthouse_location
		self.location_collection = LocationCollection(self.locations_by_id)


	def setup_items(self):
		self.book = Item(1105, 0x2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper", {}, None)
		lamp_list_templates = {ListTemplateType.DEFAULT, "{0} (currently {1})"}
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x100A, Labels("lamp", "a lamp", "a small lamp"), 2, None, lamp_list_templates, "{0} ({1})", lamp_switching_info)
		suit_list_templates = {ListTemplateType.USING, "(wearing) {0}"}
		self.suit = UsableItem(1046, 0x402, Labels("suit", "a suit", "a space-suit"), 2, None, suit_list_templates, None, "{0} (being worn)", Item.ATTRIBUTE_GIVES_AIR)
		self.items_by_id = {
			1105 : self.book,
			1043 : self.lamp,
			1046 : self.suit,
		}
		self.item_collection = ItemCollection({}, self.items_by_id)


	def test_validate_valid(self):
		validation = self.validator.validate(self.data_collection)

		self.assertFalse(validation)


	def test_validate_command_teleport_no_teleport_info(self):
		self.commands_by_id.clear()
		self.commands_by_id[51] = Command(51, 0x2, [], [], ["teleport"],  {})

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Command {0} \"{1}\" is a teleport command, but no teleport info has been given. No teleports will be possible.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((51, "teleport"), validation_line.args)


	def test_validate_command_non_teleport_with_teleport_info(self):
		self.commands_by_id.clear()
		take_command = Command(56, 0x0, [], [], ["take", "t"],  {})
		self.commands_by_id[56] = take_command
		take_command.teleport_info[6] = self.lighthouse_location

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Command {0} \"{1}\" is not a teleport command, but teleport info has been given. This teleport info will be ignored.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((56, "take"), validation_line.args)


	def test_validate_command_switchable_no_switch_info(self):
		self.commands_by_id.clear()
		self.commands_by_id[63] = Command(63, 0x100, [], [], ["verbose"], {})

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Command {0} \"{1}\" is a switchable command, but no switch info has been given.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((63, "verbose"), validation_line.args)


	def test_validate_command_non_switchable_with_switch_info(self):
		self.commands_by_id.clear()
		switch_info = {"off" : False, "on" : True}
		self.commands_by_id[56] = Command(56, 0x0, [], [], ["take", "t"],  switch_info)

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Command {0} \"{1}\" is not a switchable command, but switch info has been given. This switch info will be ignored.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((56, "take"), validation_line.args)


	def test_validate_inventory_no_inventories(self):
		self.inventories_by_id.clear()

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("No inventories specified. At least one inventory must be given.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((), validation_line.args)


	def test_validate_inventory_no_default(self):
		self.inventories_by_id.clear()
		self.inventories_by_id[1] = Inventory(1, 0x0, Labels("Special Inventory", "in the special inventory", ", where items live sometimes."), 3, [12])

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(self.inventories_by_id))
		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("No default inventory found. Exactly one inventory must be marked as default.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((), validation_line.args)


	def test_validate_inventory_multiple_defaults(self):
		self.inventories_by_id[1] = Inventory(1, 0x1, Labels("Special Inventory", "in the special inventory", ", where items live sometimes."), 3)

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(2, len(self.inventories_by_id))
		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Multiple default inventories found ({0}). Exactly one inventory must be marked as default.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual(([0, 1],), validation_line.args)


	def test_validate_inventory_default_with_locations(self):
		self.inventories_by_id.clear()
		self.inventories_by_id[1] = Inventory(0, 0x1, Labels("Main Inventory", "in the main inventory", ", where items live usually."), 3, [12])

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(self.inventories_by_id))
		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual( "Default inventory {0} \"{1}\" has location ids specified. This is redundant.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((0, "Main Inventory"), validation_line.args)


	def test_validate_inventory_non_default_no_locations(self):
		self.inventories_by_id[1] = Inventory(1, 0x0, Labels("Special Inventory", "in the special inventory", ", where items live sometimes."), 3)

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(2, len(self.inventories_by_id))
		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Non-default inventory {0} \"{1}\" has no location ids specified. It will not be used anywhere.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((1, "Special Inventory"), validation_line.args)


	def test_validate_inventory_non_default_unknown_location(self):
		self.inventories_by_id[1] = Inventory(1, 0x0, Labels("Special Inventory", "in the special inventory", ", where items live sometimes."), 3, [888])

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(2, len(self.inventories_by_id))
		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Non-default inventory {0} \"{1}\" references location with id {2}, but this does not reference a valid location.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1, "Special Inventory", 888), validation_line.args)


	def test_validate_inventory_non_default_duplicate_location(self):
		self.inventories_by_id[1] = Inventory(1, 0x0, Labels("Special Inventory", "in the special inventory", ", where items live sometimes."), 3, [12, 12])

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(2, len(self.inventories_by_id))
		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Non-default inventory {0} \"{1}\" references location with id {2} multiple times.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((1, "Special Inventory", 12), validation_line.args)


	def test_validate_inventory_non_default_shared_location(self):
		self.inventories_by_id[1] = Inventory(1, 0x0, Labels("Special Inventory", "in the special inventory", ", where items live sometimes."), 3, [12])
		self.inventories_by_id[2] = Inventory(2, 0x0, Labels("Occasional Inventory", "in the occasional inventory", ", where items live occasionally."), 3, [12])

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(3, len(self.inventories_by_id))
		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Non-default inventory {0} \"{1}\" references location with id {2}, but this location is referenced by at least one other inventory.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((2, "Occasional Inventory", 12), validation_line.args)


	def test_validate_location_no_floor_no_down(self):
		self.locations_by_id[17] = Location(17, 0x50F, Labels("Precipice", "on a precipice", ", high in the air"))

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Location {0} has no floor, but does not specify a link in direction {1}.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((17, "DOWN"), validation_line.args)


	def test_validate_location_no_land_no_floor(self):
		mid_air_location = Location(19, 0x10F, Labels("Mid-air", "in mid-air", "; you are not sure how high"))
		mid_air_location.directions[Direction.DOWN] = self.lighthouse_location
		self.locations_by_id[19] = mid_air_location

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Location {0} has no land, but also no floor. Locations without land must have a floor.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((19,), validation_line.args)


	def test_validate_item_switchable_no_list_templates(self):
		button_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "up", "down")
		self.items_by_id[1044] = SwitchableItem(1044, 0x8, Labels("button", "a button", "a red button", [". It is dark", ". It is glowing"]), 2, None, {}, "{0} ({1})", button_switching_info)

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Missing or incomplete list templates found for switchable item {0} \"{1}\". While not mandatory, this will lead to incomplete descriptions of this item when listed. Switchable items should specify either \"default\" or both \"location\" and \"carrying\" list templates.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((1044, "button"), validation_line.args)


	def test_validate_item_switchable_incomplete_list_templates(self):
		button_list_templates = {ListTemplateType.LOCATION, "{0} (currently {1})"}
		button_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "up", "down")
		self.items_by_id[1044] = SwitchableItem(1044, 0x8, Labels("button", "a button", "a red button", [". It is dark", ". It is glowing"]), 2, None, button_list_templates, "{0} ({1})", button_switching_info)

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Missing or incomplete list templates found for switchable item {0} \"{1}\". While not mandatory, this will lead to incomplete descriptions of this item when listed. Switchable items should specify either \"default\" or both \"location\" and \"carrying\" list templates.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((1044, "button"), validation_line.args)


	def test_validate_item_usable_no_list_template_using(self):
		self.items_by_id[1118] = UsableItem(1118, 0x10000, Labels("raft", "a raft", "a rickety raft"), 6, None, {}, None, None, Item.ATTRIBUTE_GIVES_LAND)

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Mandatory list template \"using\" not found for usable item {0} \"{1}\".", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1118, "raft"), validation_line.args)


if __name__ == "__main__":
	unittest.main()
