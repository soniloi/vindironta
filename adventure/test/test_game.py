import unittest
from unittest.mock import patch

from adventure.game import Game
from adventure import file_reader

class TestGame(unittest.TestCase):

	def test_init_commands(self):
		with patch(file_reader.__name__ + ".FileReader") as reader_mock:
			reader_mock_instance = reader_mock.return_value
			reader_mock_instance.read_line.side_effect = [
				"50\t0\tscore\tscore",
				"56\t0C\ttake\ttake,t,get,fetch",
				"---",
			]

			game = Game()
			game.init_commands(reader_mock_instance)

			self.assertEqual(5, len(game.commands))
			self.assertTrue("score" in game.commands)
			self.assertTrue("take" in game.commands)
			self.assertTrue("t" in game.commands)
			self.assertTrue("get" in game.commands)
			self.assertTrue("fetch" in game.commands)

			score_command = game.commands["score"]
			take_command = game.commands["take"]
			t_command = game.commands["t"]
			get_command = game.commands["get"]
			fetch_command = game.commands["fetch"]

			self.assertIsNot(score_command, take_command)
			self.assertIs(take_command, t_command)
			self.assertIs(take_command, get_command)
			self.assertIs(take_command, fetch_command)


	def test_process_input_empty(self):
		game = Game()

		response = game.process_input([])

		self.assertEqual("", response)


	def test_process_input_command_empty(self):
		game = Game()

		response = game.process_input([""])

		self.assertEqual("", response)


	def test_process_input_command_unknown(self):
		game = Game()

		response = game.process_input(["notacommand"])

		self.assertEqual("", response)


	def test_process_input_command_known(self):
		game = Game()

		response = game.process_input(["look"])

		self.assertEqual("You cannot see at thing in this darkness", response)


if __name__ == "__main__":
 	unittest.main()
