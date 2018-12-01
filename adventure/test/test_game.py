import unittest
from unittest.mock import Mock

from adventure.data_collection import DataCollection
from adventure.data_element import Labels
from adventure.game import Game
from adventure.inventory import Inventory
from adventure.location import Location

class TestGame(unittest.TestCase):

	def setUp(self):
		data = self.setup_data()
		commands = self.setup_commands()
		self.setup_responses()
		self.game = self.setup_game(data, commands)


	def setup_data(self):

		self.setup_inventories()

		data = Mock()
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
		commands = Mock()
		commands.get.side_effect = self.command_side_effect

		die_command = Mock()
		die_command.execute.side_effect = self.die_side_effect
		look_command = Mock()
		look_command.execute.return_value = "You cannot see a thing."
		self.take_command = Mock()
		self.take_command.execute.return_value = "Taken."
		switch_command = Mock()
		switch_command.execute.return_value = "Switched."

		self.command_map = {
			"die" : die_command,
			"look" : look_command,
			"switch" : switch_command,
		}

		return commands


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
		self.game.player.alive = False
		return "You have died."


	def setup_game(self, data, commands):
		game = Game()
		game.data = data
		game.commands = commands
		game.init_player()

		return game


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


	def test_init_player(self):
		self.assertEqual(self.initial_location, self.game.player.location)

		# TODO: fix
		default_inventory = self.game.player.default_inventory
		self.assertIsNot(self.default_inventory_template, default_inventory)
		self.assertEqual(self.default_inventory_template.data_id, default_inventory.data_id)
		self.assertEqual(self.default_inventory_template.attributes, default_inventory.attributes)
		self.assertEqual(self.default_inventory_template.capacity, default_inventory.capacity)
		self.assertEqual(0, len(default_inventory.items))

		non_default_inventories = self.game.player.inventories_by_location
		self.assertEqual(3, len(non_default_inventories))
		self.assertTrue(37 in non_default_inventories)
		self.assertTrue(38 in non_default_inventories)
		self.assertTrue(39 in non_default_inventories)
		non_default_inventory_37 = non_default_inventories[37]
		self.assertIsNot(self.non_default_inventory_template, non_default_inventory_37)
		self.assertIs(non_default_inventory_37, non_default_inventories[38])
		self.assertIs(non_default_inventory_37, non_default_inventories[39])
		self.assertEqual(self.non_default_inventory_template.capacity, non_default_inventory_37.capacity)


	def test_process_input_empty(self):
		response = self.game.process_input("")

		self.assertEqual("", response)
		self.assertEqual(0, self.game.player.instructions)


	def test_process_input_command_unknown(self):
		response = self.game.process_input("notacommand")

		self.assertEqual("Switched.", response)
		self.assertEqual(1, self.game.player.instructions)


	def test_process_input_command_known(self):
		response = self.game.process_input("look")

		self.assertEqual("You cannot see a thing.", response)
		self.assertEqual(1, self.game.player.instructions)


	def test_process_input_command_known_uppercase(self):
		response = self.game.process_input("LOOK")

		self.assertEqual("You cannot see a thing.", response)
		self.assertEqual(1, self.game.player.instructions)


	def test_process_input_command_known_extra_arg(self):
		response = self.game.process_input("look here")

		self.assertEqual("You cannot see a thing.", response)
		self.assertEqual(1, self.game.player.instructions)


	def test_process_input_command_current(self):
		self.game.player.current_command = self.take_command

		response = self.game.process_input("lamp")

		self.assertEqual("Taken.", response)
		self.assertEqual(0, self.game.player.instructions)


	def test_process_input_command_causes_death(self):
		response = self.game.process_input("die")

		self.assertEqual("You have died. You are dead. I may be able to reincarnate you. Do you want to be reincarnated?", response)
		self.assertFalse(self.game.player.alive)
		self.assertTrue(self.game.player.playing)
		self.assertTrue(self.game.on)


	def test_process_input_reincarnation_true(self):
		self.game.player.alive = False
		self.game.player.previous_location = self.initial_location
		self.game.player.location = self.beach_location

		response = self.game.process_input("yes")

		self.assertEqual("You have been reincarnated.", response)
		self.assertTrue(self.game.player.alive)
		self.assertTrue(self.game.player.playing)
		self.assertTrue(self.game.on)
		self.assertEqual(self.initial_location, self.game.player.location)
		self.assertIsNone(self.game.player.previous_location)


	def test_process_input_reincarnation_false(self):
		self.game.player.alive = False

		response = self.game.process_input("n")

		self.assertEqual("OK.", response)
		self.assertFalse(self.game.player.alive)
		self.assertFalse(self.game.player.playing)
		self.assertFalse(self.game.on)


	def test_process_input_reincarnation_invalid(self):
		self.game.player.alive = False

		response = self.game.process_input("xyz")

		self.assertEqual("I do not understand. Do you want to be reincarnated?", response)
		self.assertFalse(self.game.player.alive)
		self.assertTrue(self.game.player.playing)
		self.assertTrue(self.game.on)


if __name__ == "__main__":
 	unittest.main()
