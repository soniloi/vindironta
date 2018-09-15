import unittest
from unittest.mock import patch

from adventure.location_collection import LocationCollection
from adventure import file_reader

class TestLocationCollection(unittest.TestCase):

	def setUp(self):
		with patch(file_reader.__name__ + ".FileReader") as reader_mock:
			reader_mock_instance = reader_mock.return_value
			reader_mock_instance.read_line.side_effect = [
				"9\t0\t7\t0\t0\t0\t0\t0\t0\t0\t0\t70F\tWard\tin a medical ward\t. The faint electric light is flickering on and off, but it is enough to see by. The exit is to the south\t.\t.",
				"25\t34\t0\t0\t0\t0\t0\t26\t0\t0\t0\t70E\tKitchen\tin the kitchen\t. A lovely aroma of lentil soup lingers in the air. There are doors to the north and southeast\t.\t.",
				"---",
			]

			self.collection = LocationCollection(reader_mock_instance)


	def test_init(self):
		self.assertEqual(2, len(self.collection.locations))
		self.assertTrue(9 in self.collection.locations)
		self.assertTrue(25 in self.collection.locations)

		ward_location = self.collection.locations[9]
		self.assertEqual(0x70F, ward_location.attributes)
		self.assertEqual("Ward", ward_location.shortname)
		self.assertEqual("in a medical ward", ward_location.longname)
		self.assertEqual(". The faint electric light is flickering on and off, but it is enough to see by. The exit is to the south", ward_location.description)

		kitchen_location = self.collection.locations[25]
		self.assertIsNot(ward_location, kitchen_location)


if __name__ == "__main__":
	unittest.main()
