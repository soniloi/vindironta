import io
import unittest
from unittest.mock import Mock

from cli.cli import Cli

class TestCli(unittest.TestCase):

	def setUp(self):
		self.cli = Cli()
		self.output = io.StringIO()


	def tearDown(self):
		self.output.close()


	def test_run_game_not_running(self):
		game = Mock()
		game.get_start_message.return_value = "Welcome to the game!"
		game.is_running.return_value = False

		self.cli.run(game, self.output)

		self.assertEqual("\x1b[32m> Welcome to the game!\n\x1b[0m", self.output.getvalue())


if __name__ == "__main__":
	unittest.main()
