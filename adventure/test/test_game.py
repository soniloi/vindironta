import unittest
from unittest.mock import Mock
from unittest.mock import patch

from adventure import command
from adventure import command_collection
from adventure.data_collection import DataCollection
from adventure.game import Game
from adventure import location_collection

class TestGame(unittest.TestCase):

	def setUp(self):
		self.game = Game()

		with patch(command_collection.__name__ + ".CommandCollection") as command_collection_mock:
			self.command_collection_mock_instance = command_collection_mock.return_value
			self.command_collection_mock_instance.get.side_effect = self.command_side_effect
		self.game.command_collection = self.command_collection_mock_instance

		look_command = Mock()
		look_command.execute.return_value = "You cannot see a thing."

		self.take_command = Mock()
		self.take_command.execute.return_value = "Taken."

		self.command_map = {
			"look" : look_command
		}

		with patch(location_collection.__name__ + ".LocationCollection") as location_collection_mock:
			self.location_collection_mock_instance = location_collection_mock.return_value
			self.location_collection_mock_instance.get.side_effect = self.location_side_effect
		self.game.location_collection = self.location_collection_mock_instance
		self.initial_location_instance = Mock()
		self.location_map = {
			9 : self.initial_location_instance
		}

		self.game.data = DataCollection(None, self.location_collection_mock_instance, None, None, None, None, None)
		self.game.init_player()


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


	def test_init_player(self):
		self.assertEqual(self.initial_location_instance, self.game.player.location)
		# TODO: fix this assertion
		self.assertEqual(0, len(self.game.player.inventory.items))


	def test_process_input_empty(self):
		response = self.game.process_input("")

		self.assertEqual("", response)


	def test_process_input_command_unknown(self):
		response = self.game.process_input("notacommand")

		self.assertEqual("", response)


	def test_process_input_command_known(self):
		response = self.game.process_input("look")

		self.assertEqual("You cannot see a thing.", response)


	def test_process_input_command_known_extra_arg(self):
		response = self.game.process_input("look here")

		self.assertEqual("You cannot see a thing.", response)


	def test_process_input_command_current(self):
		self.game.player.current_command = self.take_command

		response = self.game.process_input("lamp")

		self.assertEqual("Taken.", response)


if __name__ == "__main__":
 	unittest.main()
