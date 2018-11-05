import unittest
from unittest.mock import Mock

from adventure.argument_resolver import ArgumentResolver
from adventure.command import Command
from adventure.command_collection import CommandCollection
from adventure.command_handler import CommandHandler
from adventure import file_reader
from adventure.location import Location
from adventure.player import Player
from adventure.resolvers import Resolvers
from adventure.vision_resolver import VisionResolver

class TestCommandCollection(unittest.TestCase):

	def setUp(self):
		self.argument_resolver = ArgumentResolver()
		self.command_handler = CommandHandler()
		self.vision_resolver = VisionResolver()
		self.resolvers = Resolvers(
			vision_resolver=self.vision_resolver,
			argument_resolver=self.argument_resolver,
			command_handler=self.command_handler
		)


	def test_init_command_different_commands(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"50\t0\t\tscore\tscore\t",
			"81\t10\t\tlook\tlook\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertEqual(2, len(collection.commands))
		self.assertTrue("score" in collection.commands)
		self.assertTrue("look" in collection.commands)

		score_command = collection.commands["score"]
		look_command = collection.commands["look"]
		self.assertIsNot(score_command, look_command)


	def test_init_command_aliases(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"33\t80\t\tlook\tlook,l\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertEqual(2, len(collection.commands))
		self.assertTrue("look" in collection.commands)
		self.assertTrue("l" in collection.commands)

		look_command = collection.commands["look"]
		l_command = collection.commands["l"]
		self.assertIs(look_command, l_command)


	def test_init_non_existent_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1000\t0\t\tnotacommand\tnotacommand\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertEqual(0, len(collection.commands))


	def test_init_movement_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"16\t40\t\tgo\teast\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertTrue("east" in collection.commands)
		east_command = collection.commands["east"]
		self.assertEqual(self.argument_resolver.resolve_movement, east_command.arg_function)


	def test_init_switchable_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"116\t100\t1\tverbose\tverbose\tno,yes",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertTrue("verbose" in collection.commands)
		verbose_command = collection.commands["verbose"]
		self.assertIn("no", verbose_command.transitions)
		self.assertIn("yes", verbose_command.transitions)
		self.assertFalse(verbose_command.transitions["no"])
		self.assertTrue(verbose_command.transitions["yes"])
		self.assertEqual(self.argument_resolver.resolve_switchable, verbose_command.arg_function)


	def test_init_argless_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"50\t0\t\tscore\tscore\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertTrue("score" in collection.commands)
		score_command = collection.commands["score"]
		self.assertEqual(self.argument_resolver.resolve_argless, score_command.arg_function)


	def test_init_single_arg_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"56\t0C\t7\ttake\ttake\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertTrue("take" in collection.commands)
		take_command = collection.commands["take"]
		self.assertEqual(self.argument_resolver.resolve_args, take_command.arg_function)


	def test_init_multiple_arg_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"57\t0C\tB,F\tinsert\tinsert\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertTrue("insert" in collection.commands)
		insert_command = collection.commands["insert"]
		self.assertEqual(self.argument_resolver.resolve_args, insert_command.arg_function)
		self.assertEqual(2, len(insert_command.arg_infos))


	def test_init_resolve_vision_light_and_dark(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"81\t410\t\tlook\tlook\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		look_command = collection.commands["look"]
		self.assertEqual(self.vision_resolver.resolve_light_and_dark, look_command.vision_function)


	def test_init_resolve_vision_dark(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"82\t60C\t\tread\tread\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		read_command = collection.commands["read"]
		self.assertEqual(self.vision_resolver.resolve_dark, read_command.vision_function)


	def test_init_resolve_vision_none(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"50\t0\t\tscore\tscore\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		score_command = collection.commands["score"]
		self.assertEqual(self.vision_resolver.resolve_none, score_command.vision_function)


	def test_list_commands(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect= [
			"33\t80\t\tlook\tlook,l\t",
			"50\t0\t\tscore\tscore\t",
			"16\t40\t\tgo\teast,e\t",
			"56\t0C\t7\ttake\ttake\t",
			"1000\t0\t\tnotacommand\tnotacommand\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertEqual("e/east, l/look, score, take", collection.list_commands())


if __name__ == "__main__":
	unittest.main()
