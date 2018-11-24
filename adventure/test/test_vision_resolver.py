import unittest
from unittest.mock import Mock

from adventure.command import Command
from adventure.data_collection import DataCollection
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


	def arg_function(self, command, player, arg):
		return "{0} success!", arg


	def test_resolve_light_and_dark_player_has_light_and_needs_no_light(self):
		player = Mock()
		player.has_light_and_needs_no_light.return_value = True
		command = Command(1, 0x9, 0x0, self.arg_function, None, None, "", [], None, None, {})

		response = self.resolver.resolve_light_and_dark(command, player, "")

		self.assertEqual(("It is too bright.", ""), response)


	def test_resolve_light_and_dark_player_has_no_light_and_needs_light(self):
		player = Mock()
		player.has_light_and_needs_no_light.return_value = False
		player.has_light.return_value = False
		command = Command(1, 0x9, 0x0, self.arg_function, None, None, "", [], None, None, {})

		response = self.resolver.resolve_light_and_dark(command, player, "")

		self.assertEqual(("It is too dark.", ""), response)


	def test_resolve_light_and_dark_player_has_suitable_light(self):
		player = Mock()
		player.has_light_and_needs_no_light.return_value = False
		player.has_light.return_value = True
		command = Command(1, 0x9, 0x0, self.arg_function, None, None, "", [], None, None, {})

		response = self.resolver.resolve_light_and_dark(command, player, "")

		self.assertEqual(("{0} success!", ""), response)


	def test_resolve_dark_player_has_no_light_and_needs_light(self):
		player = Mock()
		player.has_light_and_needs_no_light.return_value = False
		player.has_light.return_value = False
		command = Command(1, 0x9, 0x0, self.arg_function, None, None, "", [], None, None, {})

		response = self.resolver.resolve_dark(command, player, "")

		self.assertEqual(("It is too dark.", ""), response)


	def test_resolve_dark_player_has_suitable_light(self):
		player = Mock()
		player.has_light_and_needs_no_light.return_value = False
		player.has_light.return_value = True
		command = Command(1, 0x9, 0x0, self.arg_function, None, None, "", [], None, None, {})

		response = self.resolver.resolve_dark(command, player, "")

		self.assertEqual(("{0} success!", ""), response)


if __name__ == "__main__":
	unittest.main()
