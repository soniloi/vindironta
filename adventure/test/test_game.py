import unittest
from unittest.mock import Mock

from adventure.data_collection import DataCollection
from adventure.game import Game
from adventure.location import Location

class TestGame(unittest.TestCase):

	def setUp(self):
		data = self.setup_data()
		commands = self.setup_commands()
		self.setup_responses()
		self.game = self.setup_game(data, commands)


	def setup_data(self):
		data = Mock()
		data.get_location.side_effect = self.location_side_effect
		data.get_response.side_effect = self.response_side_effect

		self.initial_location = Location(12, 0x1, "Lighthouse", "at a lighthouse", " by the sea.")
		self.location_map = {
			9 : self.initial_location
		}

		return data


	def setup_commands(self):
		commands = Mock()
		commands.get.side_effect = self.command_side_effect

		die_command = Mock()
		die_command.execute.side_effect = self.die_side_effect
		look_command = Mock()
		look_command.execute.return_value = "You cannot see a thing."
		self.take_command = Mock()
		self.take_command.execute.return_value = "Taken."

		self.command_map = {
			"die" : die_command,
			"look" : look_command
		}

		return commands


	def setup_responses(self):
		self.response_map = {
			"describe_dead" : "You are dead.",
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


	def location_side_effect(self, *args):
		location_id = int(args[0])
		if location_id in self.location_map:
			return self.location_map[location_id]
		return None


	def response_side_effect(self, *args):
		return self.response_map.get(args[0])


	def test_init_player(self):
		self.assertEqual(self.initial_location, self.game.player.location)
		# TODO: fix this assertion
		self.assertEqual(0, len(self.game.player.inventory.items))


	def test_process_input_empty(self):
		response = self.game.process_input("")

		self.assertEqual("", response)
		self.assertEqual(0, self.game.player.instructions)


	def test_process_input_command_unknown(self):
		response = self.game.process_input("notacommand")

		self.assertEqual("", response)
		self.assertEqual(1, self.game.player.instructions)


	def test_process_input_command_known(self):
		response = self.game.process_input("look")

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


	def test_process_input_causes_death(self):
		response = self.game.process_input("die")

		self.assertEqual("You have died. You are dead.", response)
		self.assertEqual(1, self.game.player.instructions)


if __name__ == "__main__":
 	unittest.main()
