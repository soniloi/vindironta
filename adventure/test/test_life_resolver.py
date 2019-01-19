import unittest
from unittest.mock import Mock

from adventure.command import Command
from adventure.life_resolver import LifeResolver
from adventure.player import Player

class TestLifeResolver(unittest.TestCase):

	def setUp(self):
		self.setup_data()
		self.setup_player()

		self.resolver = LifeResolver()
		self.resolver.init_data(self.data)


	def setup_data(self):
		self.data = Mock()
		self.command = Command(150, 0x0, [], [], ["do"], {}, {})
		self.inventory = Mock()
		self.location = Mock()
		self.drop_location = Mock()
		self.book = Mock()
		self.setup_responses()


	def setup_responses(self):
		self.data.get_response.side_effect = lambda x: {
			"death_no_air" : "You have no air to breathe.",
			"describe_dead" : "You are dead.",
			"describe_reincarnation" : "I may be able to reincarnate you.",
		}.get(x)


	def setup_player(self):
		self.player = Player(1, 0x3, self.location, self.inventory)
		self.player.drop_location = self.drop_location


	def test_resolve_life_player_has_no_air(self):
		self.player.take_item(self.book)
		self.location.gives_air.return_value = False
		self.inventory.gives_air.return_value = False

		response = self.resolver.resolve_life(self.command, self.player)

		self.assertEqual((False, ["You have no air to breathe.", "You are dead.", "I may be able to reincarnate you."], [], []), response)
		self.assertFalse(self.player.is_alive())
		self.inventory.drop_all_items.assert_called_once_with(self.drop_location)
		self.assertIs(self.drop_location, self.player.drop_location)


	def test_resolve_life_player_was_not_alive(self):
		self.location.gives_air.return_value = True
		self.inventory.gives_air.return_value = False
		self.player.set_alive(False)

		response = self.resolver.resolve_life(self.command, self.player)

		self.assertEqual((False, ["You are dead.", "I may be able to reincarnate you."], [], []), response)
		self.assertFalse(self.player.is_alive())
		self.assertIs(self.drop_location, self.player.drop_location)


	def test_resolve_life_player_does_not_die(self):
		self.location.gives_air.return_value = True
		self.inventory.gives_air.return_value = False

		response = self.resolver.resolve_life(self.command, self.player)

		self.assertEqual((True, [], [], []), response)
		self.assertTrue(self.player.is_alive())
		self.assertIs(self.location, self.player.drop_location)



if __name__ == "__main__":
	unittest.main()