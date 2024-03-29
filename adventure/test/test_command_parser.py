import json
import unittest
from unittest.mock import Mock, patch

from adventure.command_parser import CommandParser
from adventure.resolvers import Resolvers
from adventure.validation import Severity

class TestCommandParser(unittest.TestCase):

	def setUp(self):
		self.setup_vision_resolver()
		self.setup_argument_resolver()
		self.setup_command_handler()
		self.setup_event_resolver()
		self.setup_life_resolver()

		self.resolvers = Resolvers(
			vision_resolver=self.vision_resolver,
			argument_resolver=self.argument_resolver,
			command_handler=self.command_handler,
			event_resolver=self.event_resolver,
			life_resolver=self.life_resolver,
		)


	def setup_vision_resolver(self):
		self.mock_vision_pre_dark = Mock()
		self.mock_vision_pre_light_and_dark = Mock()
		self.mock_vision_post_light_and_dark = Mock()

		self.vision_resolver = Mock()
		self.vision_resolver.get_resolver_function.side_effect = lambda x: {
			"resolve_pre_dark" : self.mock_vision_pre_dark,
			"resolve_pre_light_and_dark" : self.mock_vision_pre_light_and_dark,
			"resolve_post_light_and_dark" : self.mock_vision_post_light_and_dark,
		}.get(x)


	def setup_argument_resolver(self):
		self.mock_argument_teleport = Mock()
		self.mock_argument_movement = Mock()
		self.mock_argument_switchable = Mock()
		self.mock_argument_switching = Mock()
		self.mock_argument_args = Mock()

		self.argument_resolver = Mock()
		self.argument_resolver.get_resolver_function.side_effect = lambda x: {
			"resolve_teleport" : self.mock_argument_teleport,
			"resolve_movement" : self.mock_argument_movement,
			"resolve_switchable" : self.mock_argument_switchable,
			"resolve_switching" : self.mock_argument_switching,
			"resolve_args" : self.mock_argument_args,
		}.get(x)


	def setup_command_handler(self):
		self.mock_handler_go = Mock()
		self.mock_handler_insert = Mock()
		self.mock_handler_look = Mock()
		self.mock_handler_read = Mock()
		self.mock_handler_score = Mock()
		self.mock_handler_smash = Mock()
		self.mock_handler_take = Mock()
		self.mock_handler_teleport = Mock()
		self.mock_handler_verbose = Mock()

		self.command_handler = Mock()
		self.command_handler.get_resolver_function.side_effect = lambda x: {
			"handle_go" : self.mock_handler_go,
			"handle_insert" : self.mock_handler_insert,
			"handle_look" : self.mock_handler_look,
			"handle_read" : self.mock_handler_read,
			"handle_score" : self.mock_handler_score,
			"handle_smash" : self.mock_handler_smash,
			"handle_take" : self.mock_handler_take,
			"handle_teleport" : self.mock_handler_teleport,
			"handle_verbose" : self.mock_handler_verbose,
		}.get(x)


	def setup_event_resolver(self):
		self.event_resolver = Mock()
		self.mock_resolve_event = Mock()
		self.event_resolver.get_resolver_function.return_value = self.mock_resolve_event


	def setup_life_resolver(self):
		self.life_resolver = Mock()
		self.mock_resolve_life = Mock()
		self.life_resolver.get_resolver_function.return_value = self.mock_resolve_life


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

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertEqual(2, len(collection.commands_by_name))
		self.assertEqual(2, len(collection.commands_by_id))
		self.assertTrue("score" in collection.commands_by_name)
		self.assertTrue("look" in collection.commands_by_name)

		score_command = collection.commands_by_name["score"]
		look_command = collection.commands_by_name["look"]
		self.assertIsNot(score_command, look_command)

		self.assertFalse(teleport_infos)
		self.assertFalse(validation)


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

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertEqual(2, len(collection.commands_by_name))
		self.assertEqual(1, len(collection.commands_by_id))
		self.assertTrue("look" in collection.commands_by_name)
		self.assertTrue("l" in collection.commands_by_name)

		look_command = collection.commands_by_name["look"]
		l_command = collection.commands_by_name["l"]
		self.assertIs(look_command, l_command)

		self.assertFalse(teleport_infos)
		self.assertFalse(validation)


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

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertEqual(0, len(collection.commands_by_name))
		self.assertEqual(0, len(collection.commands_by_id))
		self.assertFalse(teleport_infos)
		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Unrecognized handler {0} for command {1} \"{2}\". This command will not be available.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual(("notacommand", 1000, "notacommand"), validation_line.args)


	def test_init_movement_command(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 16, \
					\"attributes\": \"48\", \
					\"handler\": \"go\", \
					\"aliases\": [ \
						\"east\" \
					] \
				} \
			]"
		)

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertTrue("east" in collection.commands_by_name)
		east_command = collection.commands_by_name["east"]
		self.assertEqual(5, len(east_command.resolver_functions))
		self.assertEqual(self.mock_argument_movement, east_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_go, east_command.resolver_functions[1])
		self.assertEqual(self.mock_vision_post_light_and_dark, east_command.resolver_functions[2])
		self.assertEqual(self.mock_resolve_event, east_command.resolver_functions[3])
		self.assertEqual(self.mock_resolve_life, east_command.resolver_functions[4])
		self.assertFalse(teleport_infos)
		self.assertFalse(validation)


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

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertTrue("verbose" in collection.commands_by_name)
		verbose_command = collection.commands_by_name["verbose"]
		self.assertIn("no", verbose_command.switch_info)
		self.assertIn("yes", verbose_command.switch_info)
		self.assertFalse(verbose_command.switch_info["no"])
		self.assertTrue(verbose_command.switch_info["yes"])
		self.assertEqual(4, len(verbose_command.resolver_functions))
		self.assertEqual(self.mock_argument_switchable, verbose_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_verbose, verbose_command.resolver_functions[1])
		self.assertEqual(self.mock_resolve_event, verbose_command.resolver_functions[2])
		self.assertEqual(self.mock_resolve_life, verbose_command.resolver_functions[3])
		self.assertFalse(teleport_infos)
		self.assertFalse(validation)


	def test_init_teleport_command_valid(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 119, \
					\"attributes\": \"1A\", \
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

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertTrue("abrakadabra" in collection.commands_by_name)
		teleport_command = collection.commands_by_name["abrakadabra"]
		self.assertEqual(5, len(teleport_command.resolver_functions))
		self.assertEqual(self.mock_argument_teleport, teleport_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_teleport, teleport_command.resolver_functions[1])
		self.assertEqual(self.mock_vision_post_light_and_dark, teleport_command.resolver_functions[2])
		self.assertEqual(self.mock_resolve_event, teleport_command.resolver_functions[3])
		self.assertEqual(self.mock_resolve_life, teleport_command.resolver_functions[4])

		self.assertEqual(1, len(teleport_infos))
		teleport_info = teleport_infos[teleport_command]
		self.assertEqual(24, teleport_info[23])
		self.assertEqual(23, teleport_info[26])

		self.assertFalse(validation)


	def test_init_teleport_command_shared_source(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 119, \
					\"attributes\": \"1A\", \
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
							\"source\": 23, \
							\"destination\": 26 \
						} \
					] \
				} \
			]"
		)

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		teleport_command = collection.commands_by_name["abrakadabra"]
		self.assertEqual(1, len(teleport_infos))
		teleport_info = teleport_infos[teleport_command]
		self.assertEqual(24, teleport_info[23])

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Multiple destinations found for source {0} in teleport command {1} \"{2}\". Destination with id {3} will be its destination.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((23, 119, "abrakadabra", 26), validation_line.args)


	def test_init_single_arg_command(self):
		command_inputs = json.loads(
			"[ \
				{ \
				\"data_id\": 56, \
					\"attributes\": \"0\", \
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

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertTrue("take" in collection.commands_by_name)
		take_command = collection.commands_by_name["take"]
		self.assertEqual(4, len(take_command.resolver_functions))
		self.assertEqual(self.mock_argument_args, take_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_take, take_command.resolver_functions[1])
		self.assertEqual(self.mock_resolve_event, take_command.resolver_functions[2])
		self.assertEqual(self.mock_resolve_life, take_command.resolver_functions[3])
		self.assertFalse(teleport_infos)
		self.assertFalse(validation)


	def test_init_multiple_arg_command(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 57, \
					\"attributes\": \"0\", \
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

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertTrue("insert" in collection.commands_by_name)
		insert_command = collection.commands_by_name["insert"]
		self.assertEqual(4, len(insert_command.resolver_functions))
		self.assertEqual(self.mock_argument_args, insert_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_insert, insert_command.resolver_functions[1])
		self.assertEqual(self.mock_resolve_event, insert_command.resolver_functions[2])
		self.assertEqual(self.mock_resolve_life, insert_command.resolver_functions[3])
		self.assertEqual(2, len(insert_command.arg_infos))
		self.assertEqual([""], insert_command.arg_infos[0].linkers)
		self.assertEqual(["into", "in"], insert_command.arg_infos[1].linkers)
		self.assertFalse(teleport_infos)
		self.assertFalse(validation)


	def test_init_resolve_vision_pre_light_and_dark(self):
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

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		look_command = collection.commands_by_name["look"]
		self.assertEqual(5, len(look_command.resolver_functions))
		self.assertEqual(self.mock_vision_pre_light_and_dark, look_command.resolver_functions[0])
		self.assertEqual(self.mock_argument_args, look_command.resolver_functions[1])
		self.assertEqual(self.mock_handler_look, look_command.resolver_functions[2])
		self.assertEqual(self.mock_resolve_event, look_command.resolver_functions[3])
		self.assertEqual(self.mock_resolve_life, look_command.resolver_functions[4])
		self.assertFalse(teleport_infos)
		self.assertFalse(validation)


	def test_init_resolve_vision_pre_dark(self):
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

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		read_command = collection.commands_by_name["read"]
		self.assertEqual(5, len(read_command.resolver_functions))
		self.assertEqual(self.mock_vision_pre_dark, read_command.resolver_functions[0])
		self.assertEqual(self.mock_argument_args, read_command.resolver_functions[1])
		self.assertEqual(self.mock_handler_read, read_command.resolver_functions[2])
		self.assertEqual(self.mock_resolve_event, read_command.resolver_functions[3])
		self.assertEqual(self.mock_resolve_life, read_command.resolver_functions[4])
		self.assertFalse(teleport_infos)
		self.assertFalse(validation)


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


		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		score_command = collection.commands_by_name["score"]
		self.assertEqual(4, len(score_command.resolver_functions))
		self.assertEqual(self.mock_argument_args, score_command.resolver_functions[0])
		self.assertEqual(self.mock_handler_score, score_command.resolver_functions[1])
		self.assertEqual(self.mock_resolve_event, score_command.resolver_functions[2])
		self.assertEqual(self.mock_resolve_life, score_command.resolver_functions[3])
		self.assertFalse(teleport_infos)
		self.assertFalse(validation)


	def test_init_command_shared_alias_different_commands(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 50, \
					\"attributes\": \"0\", \
					\"handler\": \"score\", \
					\"aliases\": [ \
						\"score\", \
						\"s\" \
					] \
				}, \
				{ \
					\"data_id\": 51, \
					\"attributes\": \"48\", \
					\"handler\": \"go\", \
					\"aliases\": [ \
						\"south\", \
						\"s\" \
					] \
				} \
			]"
		)

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertEqual(3, len(collection.commands_by_name))
		self.assertEqual(2, len(collection.commands_by_id))
		self.assertTrue("score" in collection.commands_by_name)
		self.assertTrue("south" in collection.commands_by_name)
		self.assertTrue("s" in collection.commands_by_name)

		score_command = collection.commands_by_name["score"]
		south_command = collection.commands_by_name["south"]
		self.assertIsNot(score_command, south_command)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual("Multiple commands found with alias \"{0}\". Alias will map to command {1} \"{2}\".", validation_line.template)
		self.assertEqual(("s", 51, "south"), validation_line.args)
		self.assertIs(south_command, collection.commands_by_name["s"])


	def test_init_command_shared_alias_same_command(self):
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 51, \
					\"attributes\": \"48\", \
					\"handler\": \"go\", \
					\"aliases\": [ \
						\"south\", \
						\"s\", \
						\"s\" \
					] \
				} \
			]"
		)

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertEqual(2, len(collection.commands_by_name))
		self.assertEqual(1, len(collection.commands_by_id))
		self.assertTrue("south" in collection.commands_by_name)
		self.assertTrue("s" in collection.commands_by_name)
		self.assertIs(collection.commands_by_name["south"], collection.commands_by_name["s"])

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual("Alias \"{0}\" given twice for command {1} \"{2}\".", validation_line.template)
		self.assertEqual(("s", 51, "south"), validation_line.args)


	def test_init_command_shared_id(self):
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
					\"data_id\": 50, \
					\"attributes\": \"48\", \
					\"handler\": \"go\", \
					\"aliases\": [ \
						\"south\" \
					] \
				} \
			]"
		)

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertEqual(2, len(collection.commands_by_name))
		self.assertEqual(1, len(collection.commands_by_id))
		self.assertTrue("score" in collection.commands_by_name)
		self.assertTrue("south" in collection.commands_by_name)

		score_command = collection.commands_by_name["score"]
		south_command = collection.commands_by_name["south"]
		self.assertIsNot(score_command, south_command)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual("Multiple commands found with id {0}. Alias will map to command with primary alias \"{1}\".", validation_line.template)
		self.assertEqual((50, "south"), validation_line.args)
		self.assertIs(south_command, collection.commands_by_id[50])


	def test_init_command_smash(self):
		self.command_handler.is_smash_handler.return_value = True
		command_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 37, \
					\"attributes\": \"0\", \
					\"handler\": \"smash\", \
					\"aliases\": [ \
						\"smash\" \
					] \
				} \
			]"
		)

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertEqual(1, len(collection.commands_by_name))
		self.assertEqual(1, len(collection.commands_by_id))
		self.assertTrue("smash" in collection.commands_by_name)

		smash_command = collection.commands_by_name["smash"]
		self.assertEqual(37, collection.smash_command_ids[0])

		self.assertFalse(teleport_infos)
		self.assertFalse(validation)

		self.command_handler.is_smash_handler.assert_called_once_with(self.mock_handler_smash)


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
					\"attributes\": \"0\", \
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

		collection, teleport_infos, validation = CommandParser().parse(command_inputs, self.resolvers)

		self.assertEqual("e/east, l/look, score, take", collection.list_commands())
		validation_line = validation[0]
		self.assertEqual("Unrecognized handler {0} for command {1} \"{2}\". This command will not be available.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual(("notacommand", 1000, "notacommand"), validation_line.args)


if __name__ == "__main__":
	unittest.main()
