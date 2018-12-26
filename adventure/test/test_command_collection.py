import json
import unittest
from unittest.mock import Mock

from adventure.command import Command
from adventure.command_collection import CommandCollection
from adventure.location import Location
from adventure.player import Player
from adventure.resolvers import Resolvers

class TestCommandCollection(unittest.TestCase):

	def setUp(self):
		self.setup_vision_resolver()
		self.setup_argument_resolver()
		self.setup_command_handler()
		self.setup_puzzle_resolver()

		self.resolvers = Resolvers(
			vision_resolver=self.vision_resolver,
			argument_resolver=self.argument_resolver,
			command_handler=self.command_handler,
			puzzle_resolver=self.puzzle_resolver,
		)


	def setup_vision_resolver(self):
		self.vision_resolver = Mock()
		self.vision_resolver.get_resolver_function.side_effect = self.vision_resolver_side_effect

		self.mock_vision_dark = Mock()
		self.mock_vision_light_and_dark = Mock()

		self.vision_resolver_map = {
			"resolve_dark" : self.mock_vision_dark,
			"resolve_light_and_dark" : self.mock_vision_light_and_dark,
		}


	def setup_argument_resolver(self):
		self.argument_resolver = Mock()
		self.argument_resolver.get_resolver_function.side_effect = self.argument_resolver_side_effect

		self.mock_argument_teleport = Mock()
		self.mock_argument_movement = Mock()
		self.mock_argument_switchable = Mock()
		self.mock_argument_switching = Mock()
		self.mock_argument_args = Mock()

		self.argument_resolver_map = {
			"resolve_teleport" : self.mock_argument_teleport,
			"resolve_movement" : self.mock_argument_movement,
			"resolve_switchable" : self.mock_argument_switchable,
			"resolve_switching" : self.mock_argument_switching,
			"resolve_args" : self.mock_argument_args,
		}


	def setup_command_handler(self):
		self.command_handler = Mock()
		self.command_handler.get_resolver_function.side_effect = self.command_handler_side_effect

		self.mock_handler_go = Mock()
		self.mock_handler_insert = Mock()
		self.mock_handler_look = Mock()
		self.mock_handler_read = Mock()
		self.mock_handler_score = Mock()
		self.mock_handler_take = Mock()
		self.mock_handler_teleport = Mock()
		self.mock_handler_verbose = Mock()

		self.command_handler_map = {
			"handle_go" : self.mock_handler_go,
			"handle_insert" : self.mock_handler_insert,
			"handle_look" : self.mock_handler_look,
			"handle_read" : self.mock_handler_read,
			"handle_score" : self.mock_handler_score,
			"handle_take" : self.mock_handler_take,
			"handle_teleport" : self.mock_handler_teleport,
			"handle_verbose" : self.mock_handler_verbose,
		}


	def setup_puzzle_resolver(self):
		self.puzzle_resolver = Mock()
		self.puzzle_resolver.get_resolver_function.side_effect = self.puzzle_resolver_side_effect

		self.mock_puzzle_take = Mock()

		self.puzzle_resolver_map = {
			"handle_take" : self.mock_puzzle_take,
		}


	def vision_resolver_side_effect(self, *args):
		return self.vision_resolver_map.get(args[0])


	def argument_resolver_side_effect(self, *args):
		return self.argument_resolver_map.get(args[0])


	def command_handler_side_effect(self, *args):
		return self.command_handler_map.get(args[0])


	def puzzle_resolver_side_effect(self, *args):
		return self.puzzle_resolver_map.get(args[0])


	def test_init_command_different_commands(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 50, \
					\"attributes\": \"0\", \
					\"handler\": \"score\", \
					\"aliases\": [ \
						\"score\" \
					] \
				}, \
				{ \
					\"data_id\": 81, \
					\"attributes\": \"400\", \
					\"handler\": \"look\", \
					\"aliases\": [ \
						\"look\" \
					] \
				} \
			]"
		)

		collection = CommandCollection(command_inputs, self.resolvers)

		self.assertEqual(2, len(collection.commands))
		self.assertTrue("score" in collection.commands)
		self.assertTrue("look" in collection.commands)

		score_command = collection.commands["score"]
		look_command = collection.commands["look"]
		self.assertIsNot(score_command, look_command)


	def test_init_command_aliases(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 81, \
					\"attributes\": \"400\", \
					\"handler\": \"look\", \
					\"aliases\": [ \
						\"look\", \
						\"l\" \
					] \
				} \
			]"
		)

		collection = CommandCollection(command_inputs, self.resolvers)

		self.assertEqual(2, len(collection.commands))
		self.assertTrue("look" in collection.commands)
		self.assertTrue("l" in collection.commands)

		look_command = collection.commands["look"]
		l_command = collection.commands["l"]
		self.assertIs(look_command, l_command)


	def test_init_non_existent_command(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1000, \
					\"attributes\": \"0\", \
					\"handler\": \"notacommand\", \
					\"aliases\": [ \
						\"notacommand\" \
					] \
				} \
			]"
		)

		collection = CommandCollection(command_inputs, self.resolvers)

		self.assertEqual(0, len(collection.commands))


	def test_init_movement_command(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 16, \
					\"attributes\": \"40\", \
					\"handler\": \"go\", \
					\"aliases\": [ \
						\"east\" \
					] \
				} \
			]"
		)

		collection = CommandCollection(command_inputs, self.resolvers)

		self.assertTrue("east" in collection.commands)
		east_command = collection.commands["east"]
		self.assertEqual(2, len(east_command.resolver_functions))
		self.assertEqual(self.mock_argument_movement, east_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_go, east_command.resolver_functions[1])


	def test_init_switchable_command(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 116, \
					\"attributes\": \"100\", \
					\"argument_infos\": [ \
						{ \
							\"attributes\": \"1\", \
							\"linkers\": [] \
						} \
					], \
					\"handler\": \"verbose\", \
					\"aliases\": [ \
						\"verbose\", \
						\"verb\" \
					], \
					\"switch_info\": { \
						\"off\": \"no\", \
						\"on\": \"yes\" \
					} \
				} \
			]"
		)

		collection = CommandCollection(command_inputs, self.resolvers)

		self.assertTrue("verbose" in collection.commands)
		verbose_command = collection.commands["verbose"]
		self.assertIn("no", verbose_command.switch_info)
		self.assertIn("yes", verbose_command.switch_info)
		self.assertFalse(verbose_command.switch_info["no"])
		self.assertTrue(verbose_command.switch_info["yes"])
		self.assertEqual(2, len(verbose_command.resolver_functions))
		self.assertEqual(self.mock_argument_switchable, verbose_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_verbose, verbose_command.resolver_functions[1])


	def test_init_teleport_command(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 119, \
					\"attributes\": \"12\", \
					\"handler\": \"teleport\", \
					\"aliases\": [ \
						\"abrakadabra\" \
					], \
					\"teleport_info\": [ \
						{ \
							\"source\": 23, \
							\"destination\": 24 \
						}, \
						{ \
							\"source\": 26, \
							\"destination\": 23 \
						} \
					] \
				} \
			]"
		)

		collection = CommandCollection(command_inputs, self.resolvers)

		self.assertTrue("abrakadabra" in collection.commands)
		teleport_command = collection.commands["abrakadabra"]
		self.assertEqual(2, len(teleport_command.teleport_info))
		self.assertEqual(24, teleport_command.teleport_info[23])
		self.assertEqual(23, teleport_command.teleport_info[26])
		self.assertEqual(2, len(teleport_command.resolver_functions))
		self.assertEqual(self.mock_argument_teleport, teleport_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_teleport, teleport_command.resolver_functions[1])


	def test_init_single_arg_command(self):
		command_inputs = json.loads(
			"[ \
				{ \
				\"data_id\": 56, \
					\"attributes\": \"C\", \
					\"argument_infos\": [ \
						{ \
							\"attributes\": \"7\", \
							\"linkers\": [ \
								\"\" \
							] \
						} \
					], \
					\"handler\": \"take\", \
					\"aliases\": [ \
						\"take\" \
					] \
				} \
			]"
		)

		collection = CommandCollection(command_inputs, self.resolvers)

		self.assertTrue("take" in collection.commands)
		take_command = collection.commands["take"]
		self.assertEqual(3, len(take_command.resolver_functions))
		self.assertEqual(self.mock_argument_args, take_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_take, take_command.resolver_functions[1])
		self.assertEqual(self.mock_puzzle_take, take_command.resolver_functions[2])


	def test_init_multiple_arg_command(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 57, \
					\"attributes\": \"C\", \
					\"argument_infos\": [ \
						{ \
							\"attributes\": \"B\", \
							\"linkers\": [ \
								\"\" \
							] \
						}, \
						{ \
							\"attributes\": \"F\", \
							\"linkers\": [ \
								\"into\", \
								\"in\" \
							] \
						} \
					], \
					\"handler\": \"insert\", \
					\"aliases\": [ \
						\"insert\" \
					] \
				} \
			]"
		)

		collection = CommandCollection(command_inputs, self.resolvers)

		self.assertTrue("insert" in collection.commands)
		insert_command = collection.commands["insert"]
		self.assertEqual(2, len(insert_command.resolver_functions))
		self.assertEqual(self.mock_argument_args, insert_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_insert, insert_command.resolver_functions[1])
		self.assertEqual(2, len(insert_command.arg_infos))
		self.assertEqual([""], insert_command.arg_infos[0].linkers)
		self.assertEqual(["into", "in"], insert_command.arg_infos[1].linkers)



	def test_init_resolve_vision_light_and_dark(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 81, \
					\"attributes\": \"410\", \
					\"handler\": \"look\", \
					\"aliases\": [ \
						\"look\" \
					] \
				} \
			]"
		)

		collection = CommandCollection(command_inputs, self.resolvers)

		look_command = collection.commands["look"]
		self.assertEqual(3, len(look_command.resolver_functions))
		self.assertEqual(self.mock_vision_light_and_dark, look_command.resolver_functions[0])
		self.assertEqual(self.mock_argument_args, look_command.resolver_functions[1])
		self.assertEqual(self.mock_handler_look, look_command.resolver_functions[2])


	def test_init_resolve_vision_dark(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 82, \
					\"attributes\": \"400\", \
					\"argument_infos\": [ \
						{ \
							\"attributes\": \"F\", \
							\"linkers\": [] \
						} \
					], \
					\"handler\": \"read\", \
					\"aliases\": [ \
						\"read\" \
					] \
				} \
			]"
		)

		collection = CommandCollection(command_inputs, self.resolvers)

		read_command = collection.commands["read"]
		self.assertEqual(3, len(read_command.resolver_functions))
		self.assertEqual(self.mock_vision_dark, read_command.resolver_functions[0])
		self.assertEqual(self.mock_argument_args, read_command.resolver_functions[1])
		self.assertEqual(self.mock_handler_read, read_command.resolver_functions[2])


	def test_init_resolve_vision_none(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 50, \
					\"attributes\": \"0\", \
					\"handler\": \"score\", \
					\"aliases\": [ \
						\"score\" \
					] \
				} \
			]"
		)


		collection = CommandCollection(command_inputs, self.resolvers)

		score_command = collection.commands["score"]
		self.assertEqual(2, len(score_command.resolver_functions))
		self.assertEqual(self.mock_argument_args, score_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_score, score_command.resolver_functions[1])


	def test_list_commands(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 33, \
					\"attributes\": \"80\", \
					\"handler\": \"look\", \
					\"aliases\": [ \
						\"look\", \
						\"l\" \
					] \
				}, \
				{ \
					\"data_id\": 50, \
					\"attributes\": \"0\", \
					\"handler\": \"score\", \
					\"aliases\": [ \
						\"score\" \
					] \
				}, \
				{ \
					\"data_id\": 16, \
					\"attributes\": \"40\", \
					\"handler\": \"go\", \
					\"aliases\": [ \
						\"east\", \
						\"e\" \
					] \
				}, \
				{ \
					\"data_id\": 56, \
					\"attributes\": \"C\", \
					\"argument_infos\": [ \
						{ \
							\"attributes\": \"7\", \
							\"linkers\": [ \
								\"\" \
							] \
						} \
					], \
					\"handler\": \"take\", \
					\"aliases\": [ \
						\"take\" \
					] \
				}, \
				{ \
					\"data_id\": 1000, \
					\"attributes\": \"0\", \
					\"handler\": \"notacommand\", \
					\"aliases\": [ \
						\"notacommand\" \
					] \
				} \
			]"
		)

		collection = CommandCollection(command_inputs, self.resolvers)

		self.assertEqual("e/east, l/look, score, take", collection.list_commands())


if __name__ == "__main__":
	unittest.main()
