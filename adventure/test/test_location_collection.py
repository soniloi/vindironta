import unittest
from unittest.mock import patch

from adventure.location_collection import LocationCollection, Direction
from adventure import file_reader

class TestLocationCollection(unittest.TestCase):

	def setUp(self):
		with patch(file_reader.__name__ + ".FileReader") as reader_mock:
			reader_mock_instance = reader_mock.return_value
			reader_mock_instance.read_line.side_effect = [
				"7\t0\t0\t0\t8\t0\t0\t34\t9\t0\t33\t70F\tInfirm\tin the infirmary\t; the room is dimly-lit, presumably with emergency lighting. A door to the west leads into a dark room. Flickering light comes from the passage to the northwest, and a dim red light from one to the southeast. A foreboding stairs leads down into the darkness\t.\t.",
				"9\t0\t7\t0\t0\t0\t0\t0\t0\t0\t0\t70F\tWard\tin a medical ward\t. The faint electric light is flickering on and off, but it is enough to see by. The exit is to the south\t.\t.",
				"---",
			]

			self.collection = LocationCollection(reader_mock_instance)


	def test_init(self):
		self.assertEqual(2, len(self.collection.locations))
		self.assertTrue(7 in self.collection.locations)
		self.assertTrue(9 in self.collection.locations)

		ward_location = self.collection.locations[9]
		self.assertEqual(0x70F, ward_location.attributes)
		self.assertEqual("Ward", ward_location.shortname)
		self.assertEqual("in a medical ward", ward_location.longname)
		self.assertEqual(". The faint electric light is flickering on and off, but it is enough to see by. The exit is to the south", ward_location.description)

		infirmary_location = self.collection.locations[7]
		self.assertIsNot(ward_location, infirmary_location)

		self.assertEqual(ward_location, infirmary_location.directions[Direction.NORTHWEST])
		self.assertEqual(infirmary_location, ward_location.directions[Direction.SOUTH])
		self.assertIsNone(infirmary_location.directions[Direction.NORTH])
		self.assertIsNone(infirmary_location.directions[Direction.WEST])


if __name__ == "__main__":
	unittest.main()
