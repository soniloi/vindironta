import io
import unittest
from unittest.mock import Mock

from cli.cli import Cli

class TestCli(unittest.TestCase):

	def setUp(self):
		self.cli = Cli()
		self.game = Mock()
		self.output = io.StringIO()
		self.input = io.StringIO("question")


	def tearDown(self):
		self.output.close()
		self.input.close()


	def test_run_game_not_running(self):
		self.game.get_start_message.return_value = "Welcome to the game!"
		self.game.is_running.return_value = False

		self.cli.run(self.game, self.output)

		self.assertEqual("\x1b[32m> Welcome to the game!\n\x1b[0m", self.output.getvalue())


	def test_run_game_running(self):
		self.game.get_start_message.return_value = "Welcome to the game!"
		self.game.is_running.side_effect = [True, False]
		self.game.process_input.return_value = "answer"

		self.cli.run(self.game, self.output, self.input)

		self.assertEqual("\x1b[32m> Welcome to the game!\n\x1b[0m> \x1b[32m> answer\n\x1b[0m", self.output.getvalue())


if __name__ == "__main__":
	unittest.main()
