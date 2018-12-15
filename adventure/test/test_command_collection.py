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
			"50\t0\t\t\tscore\tscore\t\t",
			"81\t10\t\t\tlook\tlook\t\t",
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
			"33\t80\t\t\tlook\tlook,l\t\t",
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
			"1000\t0\t\t\tnotacommand\tnotacommand\t\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertEqual(0, len(collection.commands))


	def test_init_movement_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"16\t40\t\t\tgo\teast\t\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertTrue("east" in collection.commands)
		east_command = collection.commands["east"]
		self.assertEqual(2, len(east_command.resolver_functions))
		self.assertEqual(self.argument_resolver.resolve_movement, east_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_go, east_command.resolver_functions[1])


	def test_init_switchable_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"116\t100\t1\t\tverbose\tverbose\tno,yes\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertTrue("verbose" in collection.commands)
		verbose_command = collection.commands["verbose"]
		self.assertIn("no", verbose_command.transitions)
		self.assertIn("yes", verbose_command.transitions)
		self.assertFalse(verbose_command.transitions["no"])
		self.assertTrue(verbose_command.transitions["yes"])
		self.assertEqual(2, len(verbose_command.resolver_functions))
		self.assertEqual(self.argument_resolver.resolve_switchable, verbose_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_verbose, verbose_command.resolver_functions[1])


	def test_init_teleport_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"119\t12\t\t\tteleport\tabrakadabra\t\t23|24,26|23",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertTrue("abrakadabra" in collection.commands)
		teleport_command = collection.commands["abrakadabra"]
		self.assertEqual(2, len(teleport_command.teleport_locations))
		self.assertEqual(24, teleport_command.teleport_locations[23])
		self.assertEqual(23, teleport_command.teleport_locations[26])
		self.assertEqual(2, len(teleport_command.resolver_functions))
		self.assertEqual(self.argument_resolver.resolve_teleport, teleport_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_teleport, teleport_command.resolver_functions[1])


	def test_init_single_arg_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"56\t0C\t7\t\ttake\ttake\t\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertTrue("take" in collection.commands)
		take_command = collection.commands["take"]
		self.assertEqual(2, len(take_command.resolver_functions))
		self.assertEqual(self.argument_resolver.resolve_args, take_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_take, take_command.resolver_functions[1])


	def test_init_multiple_arg_command(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"57\t0C\tB,F\t,into|in\tinsert\tinsert\t\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertTrue("insert" in collection.commands)
		insert_command = collection.commands["insert"]
		self.assertEqual(2, len(insert_command.resolver_functions))
		self.assertEqual(self.argument_resolver.resolve_args, insert_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_insert, insert_command.resolver_functions[1])
		self.assertEqual(2, len(insert_command.arg_infos))
		self.assertEqual([""], insert_command.arg_infos[0].linkers)
		self.assertEqual(["into", "in"], insert_command.arg_infos[1].linkers)



	def test_init_resolve_vision_light_and_dark(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"81\t410\t\t\tlook\tlook\t\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		look_command = collection.commands["look"]
		self.assertEqual(3, len(look_command.resolver_functions))
		self.assertEqual(self.vision_resolver.resolve_light_and_dark, look_command.resolver_functions[0])
		self.assertEqual(self.argument_resolver.resolve_args, look_command.resolver_functions[1])
		self.assertEqual(self.command_handler.handle_look, look_command.resolver_functions[2])


	def test_init_resolve_vision_dark(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"82\t400\tF\t\tread\tread\t\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		read_command = collection.commands["read"]
		self.assertEqual(3, len(read_command.resolver_functions))
		self.assertEqual(self.vision_resolver.resolve_dark, read_command.resolver_functions[0])
		self.assertEqual(self.argument_resolver.resolve_args, read_command.resolver_functions[1])
		self.assertEqual(self.command_handler.handle_read, read_command.resolver_functions[2])


	def test_init_resolve_vision_none(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"50\t0\t\t\tscore\tscore\t\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		score_command = collection.commands["score"]
		self.assertEqual(2, len(score_command.resolver_functions))
		self.assertEqual(self.argument_resolver.resolve_args, score_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_score, score_command.resolver_functions[1])


	def test_list_commands(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect= [
			"33\t80\t\t\tlook\tlook,l\t\t",
			"50\t0\t\t\tscore\tscore\t\t",
			"16\t40\t\t\tgo\teast,e\t\t",
			"56\t0C\t7\t\ttake\ttake\t\t",
			"1000\t0\t\t\tnotacommand\tnotacommand\t\t",
			"---\t\t\t",
		]

		collection = CommandCollection(reader_mock, self.resolvers)

		self.assertEqual("e/east, l/look, score, take", collection.list_commands())


if __name__ == "__main__":
	unittest.main()
