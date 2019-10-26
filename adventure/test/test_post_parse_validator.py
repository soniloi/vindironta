import unittest

from adventure.command import Command
from adventure.command_collection import CommandCollection
from adventure.data_collection import DataCollection
from adventure.inventory import Inventory
from adventure.inventory_collection import InventoryCollection
from adventure.element import Labels
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
			items=None,
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
		pass


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


if __name__ == "__main__":
	unittest.main()
