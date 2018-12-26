import json
import unittest

from adventure.argument_resolver import ArgumentResolver
from adventure.command import Command
from adventure.command_collection import CommandCollection
from adventure.command_handler import CommandHandler
from adventure.location import Location
from adventure.player import Player
from adventure.puzzle_resolver import PuzzleResolver
from adventure.resolvers import Resolvers
from adventure.vision_resolver import VisionResolver

class TestCommandCollection(unittest.TestCase):

	def setUp(self):
		self.vision_resolver = VisionResolver()
		self.argument_resolver = ArgumentResolver()
		self.command_handler = CommandHandler()
		self.puzzle_resolver = PuzzleResolver()
		self.resolvers = Resolvers(
			vision_resolver=self.vision_resolver,
			argument_resolver=self.argument_resolver,
			command_handler=self.command_handler,
			puzzle_resolver=self.puzzle_resolver,
		)


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
		self.assertEqual(self.argument_resolver.resolve_movement, east_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_go, east_command.resolver_functions[1])


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
		self.assertEqual(self.argument_resolver.resolve_switchable, verbose_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_verbose, verbose_command.resolver_functions[1])


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
		self.assertEqual(self.argument_resolver.resolve_teleport, teleport_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_teleport, teleport_command.resolver_functions[1])


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
		self.assertEqual(2, len(take_command.resolver_functions))
		self.assertEqual(self.argument_resolver.resolve_args, take_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_take, take_command.resolver_functions[1])


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
		self.assertEqual(self.argument_resolver.resolve_args, insert_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_insert, insert_command.resolver_functions[1])
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
		self.assertEqual(self.vision_resolver.resolve_light_and_dark, look_command.resolver_functions[0])
		self.assertEqual(self.argument_resolver.resolve_args, look_command.resolver_functions[1])
		self.assertEqual(self.command_handler.handle_look, look_command.resolver_functions[2])


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
		self.assertEqual(self.vision_resolver.resolve_dark, read_command.resolver_functions[0])
		self.assertEqual(self.argument_resolver.resolve_args, read_command.resolver_functions[1])
		self.assertEqual(self.command_handler.handle_read, read_command.resolver_functions[2])


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
		self.assertEqual(self.argument_resolver.resolve_args, score_command.resolver_functions[0])
		self.assertEqual(self.command_handler.handle_score, score_command.resolver_functions[1])


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
