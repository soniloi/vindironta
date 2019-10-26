import unittest
from unittest.mock import Mock

from adventure.element import Labels
from adventure.token_processor import TokenProcessor
from adventure.inventory import Inventory
from adventure.location import Location

class TestTokenProcessor(unittest.TestCase):

	def setUp(self):
		self.setup_data()
		self.player = Mock()
		self.command_runner = Mock()
		self.processor = TokenProcessor(self.data, self.command_runner)
		self.setup_responses()


	def setup_data(self):
		self.data = Mock()
		self.setup_commands()
		self.setup_item_related_commands()
		self.setup_inventories()
		self.setup_locations()
		self.data.matches_input.side_effect = self.matches_input_side_effect


	def setup_commands(self):
		self.die_command = Mock()
		self.die_command.verb_is_first_arg.return_value = False

		self.look_command = Mock()
		self.look_command.verb_is_first_arg.return_value = False

		self.take_command = Mock()
		self.take_command.verb_is_first_arg.return_value = False

		self.switch_command = Mock()
		self.switch_command.verb_is_first_arg.return_value = False

		self.commands = Mock()
		self.commands.get_by_name.side_effect = lambda x: {
			"die" : self.die_command,
			"look" : self.look_command,
			"switch" : self.switch_command,
			"take" : self.take_command,
		}.get(x)

		self.data.get_commands.return_value = self.commands


	def setup_item_related_commands(self):
		self.pour_command = Mock()
		self.pour_command.verb_is_first_arg.return_value = True

		self.item_related_commands = Mock()
		self.item_related_commands.get.side_effect = lambda x: {
			"water" : self.pour_command,
		}.get(x)

		self.data.get_item_related_commands.return_value = self.item_related_commands


	def setup_inventories(self):
		default_labels = Labels("Main Inventory", "in the main inventory", ", where items live usually.")
		self.default_inventory_template = Inventory(0, 0x1, default_labels, 13)
		non_default_labels = Labels("Special Inventory", "in the special inventory", ", where items live sometimes.")
		self.non_default_inventory_template = Inventory(1, 0x0, non_default_labels, 8, [37, 38, 39])

		self.data.get_inventory_template.side_effect = lambda x: {
			0 : self.default_inventory_template,
			1 : self.non_default_inventory_template,
		}.get(x)

		self.data.get_inventory_templates.return_value = [self.default_inventory_template, self.non_default_inventory_template]


	def setup_locations(self):
		self.initial_location = Location(9, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.beach_location = Location(13, 0x1, Labels("Beach", "on a beach", " of black sand"))
		self.data.get_location.side_effect = lambda x: {
			9 : self.initial_location,
			13 : self.beach_location,
		}.get(x)


	def setup_responses(self):
		self.data.get_response.side_effect = lambda x: {
			"confirm_reincarnation" : "You have been reincarnated.",
			"confirm_quit" : "OK.",
			"reject_no_understand_selection" : "I do not understand.",
			"request_reincarnation" : "Do you want to be reincarnated?",
		}.get(x)


	def matches_input_side_effect(self, *args):
		internal_key = args[0]
		input_key = args[1]
		if internal_key == "false":
			return input_key in ["no", "n", "false"]
		elif internal_key == "true":
			return input_key in ["yes", "y", "true"]
		return False


	def test_process_tokens_unknown(self):
		self.player.get_current_command.return_value = None
		self.command_runner.run.return_value = "Done."

		response = self.processor.process_tokens(self.player, ["notacommand"])

		self.assertEqual("", response)
		self.command_runner.run.assert_not_called()
		self.player.increment_instructions.assert_called_once()


	def test_process_tokens_command_known_explicit_verb(self):
		self.player.get_current_command.return_value = None
		self.command_runner.run.return_value = "Done."

		response = self.processor.process_tokens(self.player, ["look"])

		self.assertEqual("Done.", response)
		self.command_runner.run.assert_called_once_with(self.look_command, self.player, [])
		self.player.increment_instructions.assert_called_once()


	def test_process_tokens_command_known_not_noun_as_verb(self):
		self.player.get_current_command.return_value = None
		self.command_runner.run.return_value = "Done."

		response = self.processor.process_tokens(self.player, ["take", "lamp"])

		self.assertEqual("Done.", response)
		self.command_runner.run.assert_called_once_with(self.take_command, self.player, ["lamp"])


	def test_process_tokens_item_related_command_known(self):
		self.player.get_current_command.return_value = None
		self.command_runner.run.return_value = "Done."

		response = self.processor.process_tokens(self.player, ["water"])

		self.assertEqual("Done.", response)
		self.command_runner.run.assert_called_once_with(self.pour_command, self.player, ["water"])
		self.player.increment_instructions.assert_called_once()


	def test_process_tokens_command_known_extra_arg(self):
		self.player.get_current_command.return_value = None
		self.command_runner.run.return_value = "Done."

		response = self.processor.process_tokens(self.player, ["look", "here"])

		self.assertEqual("Done.", response)
		self.command_runner.run.assert_called_once_with(self.look_command, self.player, ["here"])
		self.player.increment_instructions.assert_called_once()


	def test_process_tokens_command_current(self):
		self.player.get_current_command.return_value = self.take_command
		self.command_runner.run.return_value = "Done."

		response = self.processor.process_tokens(self.player, ["lamp"])

		self.assertEqual("Done.", response)
		self.command_runner.run.assert_called_once_with(self.take_command, self.player, ["lamp"])


	def test_process_tokens_command_causes_death(self):
		self.player.is_alive.side_effect = [True, False, False]
		self.player.get_current_command.return_value = None
		self.command_runner.run.return_value = "You have died."

		response = self.processor.process_tokens(self.player, ["die"])

		self.assertEqual("You have died. Do you want to be reincarnated?", response)
		self.command_runner.run.assert_called_once_with(self.die_command, self.player, [])
		self.player.set_playing.assert_not_called()


	def test_process_tokens_reincarnation_true(self):
		self.player.is_alive.side_effect = [False, True]

		response = self.processor.process_tokens(self.player, ["yes"])

		self.assertEqual("You have been reincarnated.", response)
		self.player.reincarnate.assert_called_once()
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
