import unittest
from unittest.mock import patch

from adventure.game import Game
from adventure import command
from adventure import command_collection

class TestGame(unittest.TestCase):

	def setUp(self):
		self.game = Game()
		with patch(command_collection.__name__ + ".CommandCollection") as command_collection_mock:
			self.command_collection_mock_instance = command_collection_mock.return_value
			self.command_collection_mock_instance.get.side_effect = self.input_side_effect
		self.game.command_collection = self.command_collection_mock_instance

		self.look_command_response = "You cannot see at thing in this darkness"
		with patch(command.__name__ + ".Command") as command_mock:
			look_command_instance = command_mock.return_value
			look_command_instance.execute.return_value = self.look_command_response
			self.command_map = {
				"look" : look_command_instance
			}

	def input_side_effect(self, *args):
		command_name = args[0]
		if command_name in self.command_map:
			return self.command_map[command_name]
		return None


	def test_process_input_empty(self):
		response = self.game.process_input("")

		self.assertEqual("", response)


	def test_process_input_command_unknown(self):
		response = self.game.process_input("notacommand")

		self.assertEqual("", response)


	def test_process_input_command_known(self):
		response = self.game.process_input("look")

		self.assertIs(self.look_command_response, response)


if __name__ == "__main__":
 	unittest.main()
