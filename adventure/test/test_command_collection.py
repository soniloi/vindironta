import unittest
from unittest.mock import patch

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
				"1000\t0\tnotacommand\tnotacommand",
				"---\t\t\t",
			]

			self.collection = CommandCollection(reader_mock_instance, CommandHandler())


	def test_init_commands(self):
		self.assertEqual(4, len(self.collection.commands))
		self.assertTrue("look" in self.collection.commands)
		self.assertTrue("l" in self.collection.commands)
		self.assertTrue("score" in self.collection.commands)
		self.assertTrue("ignore" in self.collection.commands)

		score_command = self.collection.commands["score"]
		look_command = self.collection.commands["look"]
		l_command = self.collection.commands["l"]

		self.assertIsNot(score_command, look_command)
		self.assertIs(look_command, l_command)


	def test_list_commands(self):
		result = self.collection.list_commands()

		self.assertEqual("l, look, score", result)


if __name__ == "__main__":
	unittest.main()
