import unittest

from adventure.command import Command
from adventure.command_collection import CommandCollection
from adventure.data_collection import DataCollection
from adventure.element import Labels
from adventure.location import Location
from adventure.post_parse_validator import PostParseValidator
from adventure.validation import Severity

class TestPostParseValidator(unittest.TestCase):

	def setUp(self):
		self.commands_by_id = {}
		self.command_collection = CommandCollection({}, self.commands_by_id, "command_list")
		self.lighthouse_location = Location(12, 0x603, Labels("Lighthouse", "at a lighthouse", " by the sea."))

		self.data_collection = DataCollection(
			commands=self.command_collection,
			inventories=None,
			locations=None,
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


	def test_validate_valid(self):
		self.commands_by_id[56] = Command(56, 0x0, [], [], ["take", "t"],  {})

		validation = self.validator.validate(self.data_collection)

		self.assertFalse(validation)


	def test_validate_teleport_no_teleport_info(self):
		self.commands_by_id[51] = Command(51, 0x2, [], [], ["teleport"],  {})

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Command {0} \"{1}\" is a teleport command, but no teleport info has been given. No teleports will be possible.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((51, "teleport"), validation_line.args)


	def test_validate_non_teleport_with_teleport_info(self):
		take_command = Command(56, 0x0, [], [], ["take", "t"],  {})
		self.commands_by_id[56] = take_command
		take_command.teleport_info[6] = self.lighthouse_location

		validation = self.validator.validate(self.data_collection)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Command {0} \"{1}\" is not a teleport command, but teleport info has been given. This teleport info will be ignored.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((56, "take"), validation_line.args)


if __name__ == "__main__":
	unittest.main()
