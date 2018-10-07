import unittest
from unittest.mock import patch

from adventure.argument_resolver import ArgumentResolver
from adventure.command import MovementCommand, ArgumentCommand, ArglessCommand
from adventure.command_collection import CommandCollection
from adventure.command_handler import CommandHandler
from adventure import file_reader
from adventure.location import Location
from adventure.player import Player

class TestCommandCollection(unittest.TestCase):

	def setUp(self):
		with patch(file_reader.__name__ + ".FileReader") as reader_mock:
			reader_mock_instance = reader_mock.return_value
			reader_mock_instance.read_line.side_effect = [
				"33\t80\tlook\tlook,l",
				"50\t0\tscore\tscore",
				"81\t10\tignore\tignore",
				"16\t40\tgo\teast,e",
				"56\t0C\ttake\ttake",
				"1000\t0\tnotacommand\tnotacommand",
				"---\t\t\t",
			]

			self.collection = CommandCollection(reader_mock_instance, ArgumentResolver(), CommandHandler())


	def test_init_commands(self):
		self.assertEqual(7, len(self.collection.commands))
		self.assertTrue("look" in self.collection.commands)
		self.assertTrue("l" in self.collection.commands)
		self.assertTrue("score" in self.collection.commands)
		self.assertTrue("ignore" in self.collection.commands)
		self.assertTrue("e" in self.collection.commands)
		self.assertTrue("east" in self.collection.commands)
		self.assertTrue("take" in self.collection.commands)

		score_command = self.collection.commands["score"]
		look_command = self.collection.commands["look"]
		l_command = self.collection.commands["l"]
		east_command = self.collection.commands["east"]
		take_command = self.collection.commands["take"]

		self.assertIsNot(score_command, look_command)
		self.assertIs(look_command, l_command)

		self.assertTrue(isinstance(look_command, ArglessCommand))
		self.assertTrue(isinstance(score_command, ArglessCommand))
		self.assertTrue(isinstance(east_command, MovementCommand))
		self.assertTrue(isinstance(take_command, ArgumentCommand))


	def test_list_commands(self):
		result = self.collection.list_commands()

		self.assertEqual("e/east, l/look, score, take", result)


if __name__ == "__main__":
	unittest.main()
