import json
import unittest

from adventure.element import Labels
from adventure.location import Location
from adventure.player_parser import PlayerParser

class TestPlayerParser(unittest.TestCase):

	def setUp(self):
		self.lighthouse_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.location_map = {
			12 : self.lighthouse_location,
		}


	def test_parse_none(self):
		player_inputs = json.loads(
			"[]"
		)

		with self.assertRaises(AssertionError) as assertion_error:
			PlayerParser().parse(player_inputs, self.location_map, None, [])

		self.assertEqual("Only exactly one player supported, 0 given.", assertion_error.exception.args[0])



	def test_parse_single(self):
		player_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 9000, \
					\"attributes\": \"3\", \
					\"location_id\": 12 \
				} \
			]"
		)

		player = PlayerParser().parse(player_inputs, self.location_map, None, [])

		self.assertEqual(9000, player.data_id)
		self.assertEqual(3, player.attributes)
		self.assertEqual(self.lighthouse_location, player.location)


	def test_parse_multiple(self):
		player_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 9000, \
					\"attributes\": \"3\", \
					\"location_id\": 12 \
				}, \
				{ \
					\"data_id\": 9001, \
					\"attributes\": \"5\", \
					\"location_id\": 17 \
				} \
			]"
		)

		with self.assertRaises(AssertionError) as assertion_error:
			PlayerParser().parse(player_inputs, self.location_map, None, [])

		self.assertEqual("Only exactly one player supported, 2 given.", assertion_error.exception.args[0])


if __name__ == "__main__":
	unittest.main()
