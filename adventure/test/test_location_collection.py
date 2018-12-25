import json
import unittest

from adventure.location_collection import LocationCollection, Direction

class TestLocationCollection(unittest.TestCase):

	def setUp(self):
		pass


	def test_init(self):
		location_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 7, \
					\"attributes\": \"70F\", \
					\"directions\": { \
						\"west\": 8, \
						\"southeast\": 34, \
						\"northwest\": 9, \
						\"down\": 33 \
					}, \
					\"labels\": { \
						\"shortname\": \"Infirm\", \
						\"longname\": \"in the infirmary\", \
						\"description\": \"; the room is dimly-lit, presumably with emergency lighting\" \
					} \
				}, \
				{ \
					\"data_id\": 9, \
					\"attributes\": \"70F\", \
					\"directions\": { \
						\"south\": 7 \
					}, \
					\"labels\": { \
						\"shortname\": \"Ward\", \
						\"longname\": \"in a medical ward\", \
						\"description\": \". The faint electric light is flickering on and off\" \
					} \
				} \
			]"
		)

		self.collection = LocationCollection(location_inputs)

		self.assertEqual(2, len(self.collection.locations))
		self.assertTrue(7 in self.collection.locations)
		self.assertTrue(9 in self.collection.locations)

		ward_location = self.collection.locations[9]
		self.assertEqual(0x70F, ward_location.attributes)
		self.assertEqual("Ward", ward_location.shortname)
		self.assertEqual("in a medical ward", ward_location.longname)
		self.assertEqual(". The faint electric light is flickering on and off", ward_location.description)

		infirmary_location = self.collection.locations[7]
		self.assertIsNot(ward_location, infirmary_location)

		self.assertEqual(infirmary_location, ward_location.directions[Direction.SOUTH])
		self.assertEqual(infirmary_location, ward_location.directions[Direction.OUT])

		self.assertEqual(ward_location, infirmary_location.directions[Direction.NORTHWEST])
		self.assertNotIn(Direction.NORTH, infirmary_location.directions)
		self.assertNotIn(Direction.WEST, infirmary_location.directions)
		self.assertNotIn(Direction.OUT, infirmary_location.directions)


if __name__ == "__main__":
	unittest.main()
