import json
import unittest

from adventure.command import Command
from adventure.direction import Direction
from adventure.location_parser import LocationParser
from adventure.validation import Severity

class TestLocationParser(unittest.TestCase):

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
						\"description\": \". The faint electric light is flickering on and off\", \
						\"extended_descriptions\": [ \
							\". There is no way out of this room\", \
							\". There is a hole in the wall that you can escape through\" \
						] \
					} \
				} \
			]"
		)
		command = Command(150, 0x0, [], [], ["do"], {})
		teleport_infos = {command: {7: 9, 9: 7}}

		collection, validation = LocationParser().parse(location_inputs, teleport_infos)

		self.assertEqual(2, len(collection.locations))
		self.assertTrue(7 in collection.locations)
		self.assertTrue(9 in collection.locations)

		ward_location = collection.locations[9]
		self.assertEqual(0x70F, ward_location.attributes)
		self.assertEqual("Ward", ward_location.shortname)
		self.assertEqual("in a medical ward", ward_location.longname)
		self.assertEqual(". The faint electric light is flickering on and off", ward_location.description)
		self.assertEqual(2, len(ward_location.extended_descriptions))
		self.assertEqual([". There is no way out of this room", ". There is a hole in the wall that you can escape through"], ward_location.extended_descriptions)

		infirmary_location = collection.locations[7]
		self.assertIsNot(ward_location, infirmary_location)

		self.assertEqual(infirmary_location, ward_location.directions[Direction.SOUTH])
		self.assertEqual(infirmary_location, ward_location.directions[Direction.OUT])

		self.assertEqual(ward_location, infirmary_location.directions[Direction.NORTHWEST])
		self.assertNotIn(Direction.NORTH, infirmary_location.directions)
		self.assertNotIn(Direction.WEST, infirmary_location.directions)
		self.assertNotIn(Direction.OUT, infirmary_location.directions)

		self.assertIs(infirmary_location, command.teleport_info[9])
		self.assertIs(ward_location, command.teleport_info[7])

		self.assertFalse(validation)


	def test_init_invalid_teleport_info(self):
		location_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 7, \
					\"attributes\": \"70F\", \
					\"directions\": { \
						\"northwest\": 9, \
						\"down\": 8 \
					}, \
					\"labels\": { \
						\"shortname\": \"Infirm\", \
						\"longname\": \"in the infirmary\", \
						\"description\": \"; the room is dimly-lit, presumably with emergency lighting\" \
					} \
				}, \
				{ \
					\"data_id\": 8, \
					\"attributes\": \"70F\", \
					\"directions\": { \
						\"up\": 7 \
					}, \
					\"labels\": { \
						\"shortname\": \"Morgue\", \
						\"longname\": \"in the morgue\", \
						\"description\": \", a dim place\" \
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
						\"description\": \". The faint electric light is flickering on and off\", \
						\"extended_descriptions\": [ \
							\". There is no way out of this room\", \
							\". There is a hole in the wall that you can escape through\" \
						] \
					} \
				} \
			]"
		)
		command = Command(150, 0x0, [], [], ["do"], {})
		teleport_infos = {command: {111: 9, 9: 17, 8: 8}}

		collection, validation = LocationParser().parse(location_inputs, teleport_infos)

		self.assertEqual(3, len(collection.locations))
		self.assertTrue(7 in collection.locations)
		self.assertTrue(9 in collection.locations)

		ward_location = collection.locations[9]
		self.assertEqual(0x70F, ward_location.attributes)
		self.assertEqual("Ward", ward_location.shortname)
		self.assertEqual("in a medical ward", ward_location.longname)
		self.assertEqual(". The faint electric light is flickering on and off", ward_location.description)
		self.assertEqual(2, len(ward_location.extended_descriptions))
		self.assertEqual([". There is no way out of this room", ". There is a hole in the wall that you can escape through"], ward_location.extended_descriptions)

		infirmary_location = collection.locations[7]
		self.assertIsNot(ward_location, infirmary_location)

		self.assertEqual(infirmary_location, ward_location.directions[Direction.SOUTH])
		self.assertEqual(infirmary_location, ward_location.directions[Direction.OUT])

		self.assertEqual(ward_location, infirmary_location.directions[Direction.NORTHWEST])
		self.assertNotIn(Direction.NORTH, infirmary_location.directions)
		self.assertNotIn(Direction.WEST, infirmary_location.directions)
		self.assertNotIn(Direction.OUT, infirmary_location.directions)

		self.assertEqual(3, len(validation))

		validation_line_0 = validation[0]
		self.assertEqual("Unknown source location id {0} for teleport command {1} \"{2}\". This command will be unreachable.", validation_line_0.template)
		self.assertEqual(Severity.WARN, validation_line_0.severity)
		self.assertEqual((111, 150, "do"), validation_line_0.args)

		validation_line_1 = validation[1]
		self.assertEqual("Unknown destination location id {0} for teleport command {1} \"{2}\".", validation_line_1.template)
		self.assertEqual(Severity.ERROR, validation_line_1.severity)
		self.assertEqual((17, 150, "do"), validation_line_1.args)

		validation_line_2 = validation[2]
		self.assertEqual("Source id and destination id {0} are the same for teleport command {1} \"{2}\".", validation_line_2.template)
		self.assertEqual(Severity.WARN, validation_line_2.severity)
		self.assertEqual((8, 150, "do"), validation_line_2.args)


if __name__ == "__main__":
	unittest.main()
