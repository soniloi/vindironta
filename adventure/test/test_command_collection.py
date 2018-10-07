import unittest
from unittest.mock import Mock

from adventure.argument_resolver import ArgumentResolver
from adventure.command import Command
from adventure.command_collection import CommandCollection
from adventure.command_handler import CommandHandler
from adventure import file_reader
from adventure.location import Location
from adventure.player import Player

class TestCommandCollection(unittest.TestCase):

	def setUp(self):
		self.argument_resolver = ArgumentResolver()
		self.command_handler = CommandHandler()


	def test_init_command_different_commands(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"50\t0\tscore\tscore",
			"81\t10\tlook\tlook",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.argument_resolver, self.command_handler)

		self.assertEqual(2, len(collection.commands))
		self.assertTrue("score" in collection.commands)
		self.assertTrue("look" in collection.commands)

		score_command = collection.commands["score"]
		look_command = collection.commands["look"]
		self.assertIsNot(score_command, look_command)


	def test_init_command_aliases(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"33\t80\tlook\tlook,l",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.argument_resolver, self.command_handler)

		self.assertEqual(2, len(collection.commands))
		self.assertTrue("look" in collection.commands)
		self.assertTrue("l" in collection.commands)

		look_command = collection.commands["look"]
		l_command = collection.commands["l"]
		self.assertIs(look_command, l_command)


	def test_init_non_existent_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1000\t0\tnotacommand\tnotacommand",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.argument_resolver, self.command_handler)

		self.assertEqual(0, len(collection.commands))


	def test_init_movement_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"16\t40\tgo\teast",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.argument_resolver, self.command_handler)

		self.assertTrue("east" in collection.commands)
		east_command = collection.commands["east"]
		self.assertEqual(self.argument_resolver.resolve_movement, east_command.resolver_function)


	def test_init_argless_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"50\t0\tscore\tscore",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.argument_resolver, self.command_handler)

		self.assertTrue("score" in collection.commands)
		score_command = collection.commands["score"]
		self.assertEqual(self.argument_resolver.resolve_argless, score_command.resolver_function)


	def test_init_single_arg_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"56\t0C\ttake\ttake",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.argument_resolver, self.command_handler)

		self.assertTrue("take" in collection.commands)
		take_command = collection.commands["take"]
		self.assertEqual(self.argument_resolver.resolve_single_arg, take_command.resolver_function)


	def test_list_commands(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect= [
			"33\t80\tlook\tlook,l",
			"50\t0\tscore\tscore",
			"81\t10\tlook\tlook",
			"16\t40\tgo\teast,e",
			"56\t0C\ttake\ttake",
			"1000\t0\tnotacommand\tnotacommand",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.argument_resolver, self.command_handler)

		self.assertEqual("e/east, l/look, score, take", collection.list_commands())


if __name__ == "__main__":
	unittest.main()
