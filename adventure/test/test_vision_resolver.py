import unittest
from unittest.mock import Mock

from adventure.player import Player
from adventure.vision_resolver import VisionResolver

class TestVisionResolver(unittest.TestCase):

	def setUp(self):

		data = Mock()
		data.get_response.side_effect = self.responses_side_effect

		self.response_map = {
			"reject_excess_light" : "It is too bright.",
			"reject_no_light" : "It is too dark.",
		}

		self.resolver = VisionResolver()
		self.resolver.init_data(data)


	def responses_side_effect(self, *args):
		return self.response_map.get(args[0])


	def test_resolve_light_and_dark_player_has_light_and_needs_no_light(self):
		player = Mock()
		player.has_light_and_needs_no_light.return_value = True
		command = Mock()

		response = self.resolver.resolve_light_and_dark(command, player, "test")

		self.assertEqual((False, "It is too bright.", [], []), response)


	def test_resolve_light_and_dark_player_has_no_light_and_needs_light(self):
		player = Mock()
		player.has_light_and_needs_no_light.return_value = False
		player.has_light.return_value = False
		command = Mock()

		response = self.resolver.resolve_light_and_dark(command, player, "test")

		self.assertEqual((False, "It is too dark.", [], []), response)


	def test_resolve_light_and_dark_player_has_suitable_light(self):
		player = Mock()
		player.has_light_and_needs_no_light.return_value = False
		player.has_light.return_value = True
		command = Mock()

		response = self.resolver.resolve_light_and_dark(command, player, "test")

		self.assertEqual((True, "", [], ["test"]), response)


	def test_resolve_dark_player_has_no_light_and_needs_light(self):
		player = Mock()
		player.has_light_and_needs_no_light.return_value = False
		player.has_light.return_value = False
		command = Mock()

		response = self.resolver.resolve_dark(command, player, "test")

		self.assertEqual((False, "It is too dark.", [], []), response)


	def test_resolve_dark_player_has_suitable_light(self):
		player = Mock()
		player.has_light_and_needs_no_light.return_value = False
		player.has_light.return_value = True
		command = Mock()

		response = self.resolver.resolve_dark(command, player, "test")

		self.assertEqual((True, "", [], ["test"]), response)


if __name__ == "__main__":
	unittest.main()
