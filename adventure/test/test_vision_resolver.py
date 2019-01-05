import unittest
from unittest.mock import Mock

from adventure.element import Labels
from adventure.location import Location
from adventure.player import Player
from adventure.vision_resolver import VisionResolver

class TestVisionResolver(unittest.TestCase):

	def setUp(self):

		self.setup_data()
		self.setup_player()

		self.resolver = VisionResolver()
		self.resolver.init_data(self.data)


	def setup_data(self):
		self.data = Mock()
		self.setup_commands()
		self.setup_locations()
		self.setup_responses()


	def setup_commands(self):
		self.command = Mock()


	def setup_locations(self):
		self.beach_location = Location(13, 0x1, Labels("Beach", "on a beach", " of black sand"))
		self.cave_location = Location(9, 0x0, Labels("Cave", "in a cave", ". It is dark"))
		self.lighthouse_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.mine_location = Location(11, 0x0, Labels("Mines", "in the mines", ". There are dark passages everywhere."))
		self.sun_location = Location(10, 0x11, Labels("Sun", "in the sun", ". It is hot."))


	def setup_responses(self):
		self.data.get_response.side_effect = lambda x: {
			"confirm_look" : "You are {0}.",
			"death_darkness" : "You fall to your death in the darkness.",
			"list_location" : " Nearby: {1}.",
			"reject_excess_light" : "It is too bright.",
			"reject_no_light" : "It is too dark.",
		}.get(x)


	def setup_player(self):
		self.player = Mock()


	def test_resolve_pre_light_and_dark_player_has_light_and_needs_no_light(self):
		self.player.has_light_and_needs_no_light.return_value = True

		response = self.resolver.resolve_pre_light_and_dark(self.command, self.player, "test")

		self.assertEqual((False, "It is too bright.", [], []), response)


	def test_resolve_pre_light_and_dark_player_has_no_light_and_needs_light(self):
		self.player.has_light_and_needs_no_light.return_value = False
		self.player.has_light.return_value = False

		response = self.resolver.resolve_pre_light_and_dark(self.command, self.player, "test")

		self.assertEqual((False, "It is too dark.", [], []), response)


	def test_resolve_pre_light_and_dark_player_has_suitable_light(self):
		self.player.has_light_and_needs_no_light.return_value = False
		self.player.has_light.return_value = True

		response = self.resolver.resolve_pre_light_and_dark(self.command, self.player, "test")

		self.assertEqual((True, "", [], ["test"]), response)


	def test_resolve_pre_dark_player_has_no_light_and_needs_light(self):
		self.player.has_light_and_needs_no_light.return_value = False
		self.player.has_light.return_value = False

		response = self.resolver.resolve_pre_dark(self.command, self.player, "test")

		self.assertEqual((False, "It is too dark.", [], []), response)


	def test_resolve_pre_dark_player_has_suitable_light(self):
		self.player.has_light_and_needs_no_light.return_value = False
		self.player.has_light.return_value = True

		response = self.resolver.resolve_pre_dark(self.command, self.player, "test")

		self.assertEqual((True, "", [], ["test"]), response)


	def test_resolve_post_light_and_dark_dark_to_dark_immune_off(self):
		self.player.is_immune.return_value = False
		self.player.has_light.return_value = False

		success, template, content_args, next_args = self.resolver.resolve_post_light_and_dark(self.command, self.player, self.mine_location, self.cave_location)

		self.assertFalse(success)
		self.assertEqual("You fall to your death in the darkness.", template)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.player.set_alive.assert_called_once_with(False)
		self.player.see_location.assert_not_called()


	def test_resolve_post_light_and_dark_light_to_dark_immune_off(self):
		self.player.is_immune.return_value = False
		self.player.has_light.return_value = False
		self.player.has_light_and_needs_no_light.return_value = False

		success, template, content_args, next_args = self.resolver.resolve_post_light_and_dark(self.command, self.player, self.mine_location, self.lighthouse_location)

		self.assertFalse(success)
		self.assertEqual("It is too dark.", template)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.player.set_alive.assert_not_called()
		self.player.see_location.assert_not_called()


	def test_resolve_post_light_and_dark_dark_to_dark_immune_on(self):
		self.player.is_immune.return_value = True
		self.player.has_light.return_value = False
		self.player.has_light_and_needs_no_light.return_value = False

		success, template, content_args, next_args = self.resolver.resolve_post_light_and_dark(self.command, self.player, self.mine_location, self.cave_location)

		self.assertFalse(success)
		self.assertEqual("It is too dark.", template)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.player.set_alive.assert_not_called()
		self.player.see_location.assert_not_called()


	def test_resolve_post_light_and_dark_player_has_light_and_needs_no_light(self):
		self.player.is_immune.return_value = False
		self.player.has_light.return_value = False
		self.player.has_light_and_needs_no_light.return_value = True

		success, template, content_args, next_args = self.resolver.resolve_post_light_and_dark(self.command, self.player, self.sun_location, self.lighthouse_location)

		self.assertFalse(success)
		self.assertEqual("It is too bright.", template)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.player.see_location.assert_not_called()


	def test_resolve_post_light_and_dark_player_has_no_light(self):
		self.player.is_immune.return_value = False
		self.player.has_light.return_value = False
		self.player.has_light_and_needs_no_light.return_value = False

		success, template, content_args, next_args = self.resolver.resolve_post_light_and_dark(self.command, self.player, self.mine_location, self.lighthouse_location)

		self.assertFalse(success)
		self.assertEqual("It is too dark.", template)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.player.see_location.assert_not_called()


	def test_resolve_post_light_and_dark_valid_no_items(self):
		self.player.is_immune.return_value = False
		self.player.has_light.return_value = True
		self.player.has_light_and_needs_no_light.return_value = False
		self.player.has_non_silent_items_nearby.return_value = False
		self.player.get_arrival_location_description.return_value = ["Here."]

		success, template, content_args, next_args = self.resolver.resolve_post_light_and_dark(self.command, self.player, self.beach_location, self.lighthouse_location)

		self.assertTrue(success)
		self.assertEqual("You are {0}.", template)
		self.assertEqual(["Here."], content_args)
		self.assertEqual([self.beach_location, self.lighthouse_location], next_args)
		self.player.see_location.assert_called_once()


	def test_resolve_post_light_and_dark_valid_with_items(self):
		self.player.is_immune.return_value = False
		self.player.has_light.return_value = True
		self.player.has_light_and_needs_no_light.return_value = False
		self.player.has_non_silent_items_nearby.return_value = True
		self.player.get_arrival_location_description.return_value = ["Here."]

		success, template, content_args, next_args = self.resolver.resolve_post_light_and_dark(self.command, self.player, self.beach_location, self.lighthouse_location)

		self.assertTrue(success)
		self.assertEqual("You are {0}. Nearby: {1}.", template)
		self.assertEqual(["Here."], content_args)
		self.assertEqual([self.beach_location, self.lighthouse_location], next_args)
		self.player.see_location.assert_called_once()


if __name__ == "__main__":
	unittest.main()
