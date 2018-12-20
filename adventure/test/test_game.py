import unittest
from unittest.mock import Mock

from adventure.game import Game

class TestGame(unittest.TestCase):

	def setUp(self):
		self.player = Mock()
		self.token_processor = Mock()
		self.token_processor.process_tokens.return_value = "goodbye"

		self.game = Game()
		self.game.player = self.player
		self.game.token_processor = self.token_processor


	def test_process_input_empty(self):
		response = self.game.process_input("")

		self.assertEqual("", response)
		self.token_processor.process_tokens.assert_not_called()


	def test_process_input_one_token(self):
		response = self.game.process_input("hello")

		self.assertEqual("goodbye", response)
		self.token_processor.process_tokens.assert_called_once_with(self.player, ["hello"])


	def test_process_input_two_tokens(self):
		response = self.game.process_input("hello  there   ")

		self.assertEqual("goodbye", response)
		self.token_processor.process_tokens.assert_called_once_with(self.player, ["hello", "there"])


	def test_process_input_uppercase(self):
		response = self.game.process_input("HELLO")

		self.assertEqual("goodbye", response)
		self.token_processor.process_tokens.assert_called_once_with(self.player, ["hello"])


	def test_process_input_mixed_case(self):
		response = self.game.process_input("HeLlo")

		self.assertEqual("goodbye", response)
		self.token_processor.process_tokens.assert_called_once_with(self.player, ["hello"])


	def test_process_input_player_still_playing(self):
		self.player.is_playing.return_value = True

		response = self.game.process_input("hello")

		self.assertEqual("goodbye", response)
		self.assertTrue(self.game.on)


	def test_process_input_player_not_still_playing(self):
		self.player.is_playing.return_value = False

		response = self.game.process_input("hello")

		self.assertEqual("goodbye", response)
		self.assertFalse(self.game.on)


if __name__ == "__main__":
 	unittest.main()
