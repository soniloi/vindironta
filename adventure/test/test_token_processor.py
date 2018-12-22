import unittest
from unittest.mock import Mock

from adventure.data_collection import DataCollection
from adventure.element import Labels
from adventure.token_processor import TokenProcessor
from adventure.inventory import Inventory
from adventure.location import Location

class TestTokenProcessor(unittest.TestCase):

	def setUp(self):
		data = self.setup_data()
		self.player = Mock()
		self.processor = TokenProcessor(data)
		self.setup_responses()


	def setup_data(self):

		self.setup_commands()
		self.setup_inventories()

		data = Mock()
		data.get_commands.return_value = self.commands
		data.get_inventory_template.side_effect = self.inventory_side_effect
		data.get_inventory_templates.return_value = self.inventory_map.values()
		data.get_location.side_effect = self.location_side_effect
		data.get_response.side_effect = self.response_side_effect
		data.matches_input.side_effect = self.matches_input_side_effect

		self.initial_location = Location(9, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.beach_location = Location(13, 0x1, Labels("Beach", "on a beach", " of black sand"))
		self.location_map = {
			9 : self.initial_location,
			13 : self.beach_location,
		}

		return data


	def setup_inventories(self):
		default_labels = Labels("Main Inventory", "in the main inventory", ", where items live usually.")
		self.default_inventory_template = Inventory(0, 0x1, default_labels, 13)
		non_default_labels = Labels("Special Inventory", "in the special inventory", ", where items live sometimes.")
		self.non_default_inventory_template = Inventory(1, 0x0, non_default_labels, 8, [37, 38, 39])
		self.inventory_map = {
			0 : self.default_inventory_template,
			1 : self.non_default_inventory_template,
		}


	def setup_commands(self):
		self.commands = Mock()
		self.commands.get.side_effect = self.command_side_effect

		self.die_command = Mock()
		self.die_command.verb_is_first_arg.return_value = False
		self.die_command.execute.side_effect = self.die_side_effect

		self.look_command = Mock()
		self.look_command.verb_is_first_arg.return_value = False
		self.look_command.execute.return_value = "You cannot see a thing."

		self.take_command = Mock()
		self.take_command.verb_is_first_arg.return_value = False
		self.take_command.execute.return_value = "Taken."

		self.pour_command = Mock()
		self.pour_command.verb_is_first_arg.return_value = True
		self.pour_command.execute.return_value = "Poured."

		self.switch_command = Mock()
		self.switch_command.verb_is_first_arg.return_value = False
		self.switch_command.execute.return_value = "Switched."

		self.command_map = {
			"die" : self.die_command,
			"look" : self.look_command,
			"switch" : self.switch_command,
			"take" : self.take_command,
			"water" : self.pour_command,
		}


	def setup_responses(self):
		self.response_map = {
			"confirm_reincarnation" : "You have been reincarnated.",
			"confirm_quit" : "OK.",
			"describe_dead" : "You are dead.",
			"describe_reincarnation" : "I may be able to reincarnate you.",
			"reject_no_understand_selection" : "I do not understand.",
			"request_reincarnation" : "Do you want to be reincarnated?",
		}


	def die_side_effect(self, *args):
		return "You have died."


	def command_side_effect(self, *args):
		command_name = args[0]
		if command_name in self.command_map:
			return self.command_map[command_name]
		return None


	def inventory_side_effect(self, *args):
		inventory_id = int(args[0])
		return self.inventory_map.get(inventory_id, None)


	def location_side_effect(self, *args):
		location_id = int(args[0])
		return self.location_map.get(location_id, None)


	def response_side_effect(self, *args):
		return self.response_map.get(args[0])


	def matches_input_side_effect(self, *args):
		internal_key = args[0]
		input_key = args[1]
		if internal_key == "false":
			return input_key in ["no", "n", "false"]
		elif internal_key == "true":
			return input_key in ["yes", "y", "true"]
		return False


	def test_process_tokens_command_unknown(self):
		self.player.get_current_command.return_value = None

		response = self.processor.process_tokens(self.player, ["notacommand"])

		self.assertEqual("Switched.", response)
		self.player.increment_instructions.assert_called_once()


	def test_process_tokens_command_known_explicit_verb(self):
		self.player.get_current_command.return_value = None

		response = self.processor.process_tokens(self.player, ["look"])

		self.assertEqual("You cannot see a thing.", response)
		self.player.increment_instructions.assert_called_once()



	def test_process_tokens_command_known_not_noun_as_verb(self):
		self.player.get_current_command.return_value = None

		response = self.processor.process_tokens(self.player, ["take", "lamp"])

		self.assertEqual("Taken.", response)


	def test_process_tokens_command_known_noun_as_verb(self):
		self.player.get_current_command.return_value = None

		response = self.processor.process_tokens(self.player, ["water"])

		self.assertEqual("Poured.", response)
		self.pour_command.execute.assert_called_once_with(self.player, ["water"])
		self.player.increment_instructions.assert_called_once()


	def test_process_tokens_command_known_extra_arg(self):
		self.player.get_current_command.return_value = None

		response = self.processor.process_tokens(self.player, ["look", "here"])

		self.assertEqual("You cannot see a thing.", response)
		self.player.increment_instructions.assert_called_once()


	def test_process_tokens_command_current(self):
		self.player.get_current_command.return_value = self.take_command

		response = self.processor.process_tokens(self.player, ["lamp"])

		self.assertEqual("Taken.", response)


	def test_process_tokens_command_causes_death(self):
		self.player.is_alive.side_effect = [True, False, False]
		self.player.get_current_command.return_value = None

		response = self.processor.process_tokens(self.player, ["die"])

		self.assertEqual("You have died. You are dead. I may be able to reincarnate you. Do you want to be reincarnated?", response)
		self.player.set_playing.assert_not_called()


	def test_process_tokens_reincarnation_true(self):
		self.player.is_alive.side_effect = [False, True]

		response = self.processor.process_tokens(self.player, ["yes"])

		self.assertEqual("You have been reincarnated.", response)
		self.player.set_alive.assert_called_once_with(True)
		self.player.set_location.assert_called_once_with(self.initial_location)
		self.player.set_previous_location.assert_called_once_with(None)
		self.player.set_playing.assert_not_called()


	def test_process_tokens_reincarnation_false(self):
		self.player.is_alive.side_effect = [False, True]
		self.player.is_playing.side_effect = [False]

		response = self.processor.process_tokens(self.player, ["n"])

		self.assertEqual("OK.", response)
		self.player.set_playing.assert_called_once_with(False)
		self.player.set_alive.assert_not_called()


	def test_process_tokens_reincarnation_invalid(self):
		self.player.is_alive.side_effect = [False, False]

		response = self.processor.process_tokens(self.player, ["xyz"])

		self.assertEqual("I do not understand. Do you want to be reincarnated?", response)
		self.player.set_alive.assert_not_called()
		self.player.set_playing.assert_not_called()


if __name__ == "__main__":
	unittest.main()
