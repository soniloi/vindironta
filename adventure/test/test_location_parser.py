import json
import unittest

from adventure.command import Command
from adventure.direction import Direction
from adventure.location_parser import LocationParser
from adventure.validation import Severity

class TestLocationParser(unittest.TestCase):

	def setUp(self):
		pass


	def test_init_no_teleport_info(self):
		location_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 7, \
					\"attributes\": \"70F\", \
					\"directions\": { \
						\"west\": 8, \
						\"northwest\": 9 \
					}, \
					\"labels\": { \
						\"shortname\": \"Infirm\", \
						\"longname\": \"in the infirmary\", \
						\"description\": \"; the room is dimly-lit, presumably with emergency lighting\" \
					} \
				}, \
				{ \
					\"data_id\": 8, \
					\"attributes\": \"70E\", \
					\"directions\": { \
						\"east\": 7 \
					}, \
					\"labels\": { \
						\"shortname\": \"Store\", \
						\"longname\": \"in a medical storage room\", \
						\"description\": \"; the only exit is to the east\" \
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

		collection, validation = LocationParser().parse(location_inputs, {})

		self.assertEqual(3, len(collection.locations))
		self.assertTrue(7 in collection.locations)
		self.assertTrue(8 in collection.locations)
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

		store_location = collection.locations[8]
		self.assertIsNot(ward_location, store_location)
		self.assertIsNot(infirmary_location, store_location)

		self.assertEqual(ward_location, infirmary_location.directions[Direction.NORTHWEST])
		self.assertEqual(store_location, infirmary_location.directions[Direction.WEST])
		self.assertNotIn(Direction.NORTH, infirmary_location.directions)
		self.assertNotIn(Direction.OUT, infirmary_location.directions)
		self.assertEqual(infirmary_location, ward_location.directions[Direction.SOUTH])
		self.assertEqual(infirmary_location, ward_location.directions[Direction.OUT])
		self.assertEqual(infirmary_location, store_location.directions[Direction.EAST])

		self.assertFalse(validation)


	def test_init_shared_location_ids(self):
		location_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 7, \
					\"attributes\": \"70F\", \
					\"directions\": { \
						\"down\": 7 \
					}, \
					\"labels\": { \
						\"shortname\": \"Infirm\", \
						\"longname\": \"in the infirmary\", \
						\"description\": \"; the room is dimly-lit, presumably with emergency lighting\" \
					} \
				}, \
				{ \
					\"data_id\": 7, \
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

		collection, validation = LocationParser().parse(location_inputs, {})

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Multiple locations found with id {0}.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((7,), validation_line.args)


	def test_init_unknown_link_direction(self):
		location_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 9, \
					\"attributes\": \"70F\", \
					\"directions\": { \
						\"hello\": 9 \
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

		collection, validation = LocationParser().parse(location_inputs, {})

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Unknown link direction \"{0}\" from location {1}.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual(("hello", 9), validation_line.args)


	def test_init_unknown_link_destination(self):
		location_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 9, \
					\"attributes\": \"70F\", \
					\"directions\": { \
						\"north\": 7 \
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

		collection, validation = LocationParser().parse(location_inputs, {})

		self.assertEqual(2, len(validation))
		validation_line_0 = validation[0]
		self.assertEqual("Unknown link destination {0} for direction {1} from location {2}.", validation_line_0.template)
		self.assertEqual(Severity.ERROR, validation_line_0.severity)
		self.assertEqual((7, Direction.NORTH, 9), validation_line_0.args)
		validation_line_1 = validation[1]
		self.assertEqual("Unknown link destination {0} for direction {1} from location {2}.", validation_line_1.template)
		self.assertEqual(Severity.ERROR, validation_line_1.severity)
		self.assertEqual((7, Direction.OUT, 9), validation_line_1.args)


	def test_init_teleport_info_valid(self):
		location_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 7, \
					\"attributes\": \"70F\", \
					\"directions\": { \
						\"northwest\": 9 \
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

		ward_location = collection.locations[9]
		infirmary_location = collection.locations[7]
		self.assertIs(infirmary_location, command.teleport_info[9])
		self.assertIs(ward_location, command.teleport_info[7])

		self.assertFalse(validation)


	def test_init_teleport_info_invalid_unknown_location_ids(self):
		location_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 9, \
					\"attributes\": \"70F\", \
					\"directions\": {}, \
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
		teleport_infos = {command: {111: 9, 9: 17}}

		collection, validation = LocationParser().parse(location_inputs, teleport_infos)

		self.assertEqual(2, len(validation))

		validation_line_0 = validation[0]
		self.assertEqual("Unknown source location id {0} for teleport command {1} \"{2}\". This command will be unreachable.", validation_line_0.template)
		self.assertEqual(Severity.WARN, validation_line_0.severity)
		self.assertEqual((111, 150, "do"), validation_line_0.args)

		validation_line_1 = validation[1]
		self.assertEqual("Unknown destination location id {0} for teleport command {1} \"{2}\".", validation_line_1.template)
		self.assertEqual(Severity.ERROR, validation_line_1.severity)
		self.assertEqual((17, 150, "do"), validation_line_1.args)


	def test_init_teleport_info_invalid_matching_location_ids(self):
		location_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 9, \
					\"attributes\": \"70F\", \
					\"directions\": {}, \
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
		teleport_infos = {command: {9: 9}}

		collection, validation = LocationParser().parse(location_inputs, teleport_infos)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Source id and destination id {0} are the same for teleport command {1} \"{2}\".", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((9, 150, "do"), validation_line.args)


if __name__ == "__main__":
	unittest.main()
