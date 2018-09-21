import unittest
from unittest.mock import patch

from adventure.command_handler import CommandHandler
from adventure.location import Location
from adventure.player import Player

class TestCommandHandler(unittest.TestCase):

	def setUp(self):
		self.handler = CommandHandler()
		location = Location(11, 0, "Mines", "in the mines", ". There are dark passages everywhere")
		self.player = Player(location)


	def test_handle_inventory(self):
		response = self.handler.handle_inventory(self.player)

		self.assertEqual("You are not holding anything.", response)


	def test_handle_look(self):
		response = self.handler.handle_look(self.player)

		self.assertEqual("You are in the mines. There are dark passages everywhere.", response)


	def test_handle_quit(self):
		response = self.handler.handle_quit(self.player)

		self.assertEqual("Game has ended", response)
		self.assertFalse(self.player.playing)


	def test_handle_score(self):
		response = self.handler.handle_score(self.player)

		self.assertEqual("Your current score is 0 points", response)


if __name__ == "__main__":
	unittest.main()
