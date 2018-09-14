import unittest

from adventure.game import Game

class TestGame(unittest.TestCase):

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
