import unittest
from unittest.mock import patch

from adventure.game import Game
from adventure import file_reader

class TestGame(unittest.TestCase):

	def setUp(self):
		self.game = Game()
		with patch(file_reader.__name__ + ".FileReader") as reader_mock:
			reader_mock_instance = reader_mock.return_value
			reader_mock_instance.read_line.side_effect = [
				"33\t80\tlook\tlook,l",
				"50\t0\tscore\tscore",
				"1000\t0\tnotacommand\tnotacommand",
				"---",
			]

			self.game.init_commands(reader_mock_instance)


	def test_init_commands(self):
		self.assertEqual(3, len(self.game.commands))
		self.assertTrue("look" in self.game.commands)
		self.assertTrue("l" in self.game.commands)
		self.assertTrue("score" in self.game.commands)

		score_command = self.game.commands["score"]
		look_command = self.game.commands["look"]
		l_command = self.game.commands["l"]

		self.assertIsNot(score_command, look_command)
		self.assertIs(look_command, l_command)


	def test_process_input_empty(self):
		response = self.game.process_input([])

		self.assertEqual("", response)


	def test_process_input_command_empty(self):
		response = self.game.process_input([""])

		self.assertEqual("", response)


	def test_process_input_command_unknown(self):
		response = self.game.process_input(["notacommand"])

		self.assertEqual("", response)


	def test_process_input_command_known(self):
		response = self.game.process_input(["look"])

		self.assertEqual("You cannot see at thing in this darkness", response)


if __name__ == "__main__":
 	unittest.main()
