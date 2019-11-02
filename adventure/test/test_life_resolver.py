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
		self.command = Command(150, 0x0, [], [], ["do"], {})
		self.inventory = Mock()
		self.player_location = Mock()
		self.essential_drop_location = Mock()
		self.non_essential_drop_location = Mock()
		self.collectible_location = Mock()
		self.book = Mock()


	def setup_player(self):
		self.player = Player(1, 0x3, self.player_location, self.essential_drop_location, self.player_location, self.collectible_location, self.inventory)
		self.player.drop_location = self.non_essential_drop_location
		self.player.set_immune(False)


	def test_resolve_life_player_has_no_air_not_immune(self):
		self.player.take_item(self.book)
		self.player_location.gives_air.return_value = False
		self.inventory.gives_air.return_value = False

		response = self.resolver.resolve_life(self.command, self.player)

		self.assertEqual((False, ["death_no_air", "describe_dead", "describe_reincarnation"], [], []), response)
		self.assertFalse(self.player.is_alive())
		self.inventory.drop_all_items.assert_called_once_with(self.non_essential_drop_location, self.essential_drop_location)
		self.assertIs(self.non_essential_drop_location, self.player.drop_location)


	def test_resolve_life_player_has_no_air_immune(self):
		self.player.set_immune(True)
		self.player.take_item(self.book)
		self.player_location.gives_air.return_value = False
		self.inventory.gives_air.return_value = False

		response = self.resolver.resolve_life(self.command, self.player)

		self.assertEqual((True, [], [], []), response)
		self.assertTrue(self.player.is_alive())
		self.inventory.drop_all_items.assert_not_called()
		self.assertIs(self.player_location, self.player.drop_location)


	def test_resolve_life_player_has_no_land_not_immune(self):
		self.player.take_item(self.book)
		self.player_location.gives_air.return_value = True
		self.player_location.has_land.return_value = False
		self.inventory.gives_land.return_value = False
		self.inventory.gives_gravity.return_value = False

		response = self.resolver.resolve_life(self.command, self.player)

		self.assertEqual((False, ["death_no_land", "describe_dead", "describe_reincarnation"], [], []), response)
		self.assertFalse(self.player.is_alive())
		self.inventory.drop_all_items.assert_called_once_with(self.non_essential_drop_location, self.essential_drop_location)
		self.assertIs(self.non_essential_drop_location, self.player.drop_location)


	def test_resolve_life_player_has_no_land_immune(self):
		self.player.set_immune(True)
		self.player.take_item(self.book)
		self.player_location.gives_air.return_value = True
		self.player_location.has_land.return_value = False
		self.inventory.gives_land.return_value = False
		self.inventory.gives_gravity.return_value = False

		response = self.resolver.resolve_life(self.command, self.player)

		self.assertEqual((True, [], [], []), response)
		self.assertTrue(self.player.is_alive())
		self.inventory.drop_all_items.assert_not_called()
		self.assertIs(self.player_location, self.player.drop_location)


	def test_resolve_life_player_has_no_tether_not_immune(self):
		self.player.take_item(self.book)
		self.player_location.gives_air.return_value = True
		self.player_location.has_land.return_value = True
		self.player_location.gives_tether.return_value = False
		self.inventory.gives_gravity.return_value = False

		response = self.resolver.resolve_life(self.command, self.player)

		self.assertEqual((False, ["death_untethered", "describe_dead", "describe_reincarnation"], [], []), response)
		self.assertFalse(self.player.is_alive())
		self.inventory.drop_all_items.assert_called_once_with(self.non_essential_drop_location, self.essential_drop_location)
		self.assertIs(self.non_essential_drop_location, self.player.drop_location)


	def test_resolve_life_player_has_no_tether_immune(self):
		self.player.set_immune(True)
		self.player.take_item(self.book)
		self.player_location.gives_air.return_value = True
		self.player_location.has_land.return_value = True
		self.player_location.gives_tether.return_value = False
		self.inventory.gives_gravity.return_value = False

		response = self.resolver.resolve_life(self.command, self.player)

		self.assertEqual((True, [], [], []), response)
		self.assertTrue(self.player.is_alive())
		self.inventory.drop_all_items.assert_not_called()
		self.assertIs(self.player_location, self.player.drop_location)


	def test_resolve_life_player_was_not_alive(self):
		self.player_location.gives_air.return_value = True
		self.inventory.gives_air.return_value = False
		self.player.set_alive(False)

		response = self.resolver.resolve_life(self.command, self.player)

		self.assertEqual((False, ["describe_dead", "describe_reincarnation"], [], []), response)
		self.assertFalse(self.player.is_alive())
		self.assertIs(self.non_essential_drop_location, self.player.drop_location)


	def test_resolve_life_player_does_not_die(self):
		self.player_location.gives_air.return_value = True
		self.inventory.gives_air.return_value = False

		response = self.resolver.resolve_life(self.command, self.player)

		self.assertEqual((True, [], [], []), response)
		self.assertTrue(self.player.is_alive())
		self.assertIs(self.player_location, self.player.drop_location)



if __name__ == "__main__":
	unittest.main()
