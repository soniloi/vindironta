import json
import unittest

from adventure.event import EventMatchArgumentType
from adventure.event_collection import EventCollection

class TestEventCollection(unittest.TestCase):

	def setUp(self):
		pass


	def test_event_without_args(self):
		event_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 3001, \
					\"attributes\": \"0\", \
					\"match\": { \
						\"command_id\": 48, \
						\"arguments\": [] \
					}, \
					\"outcome\": { \
						\"text\" : \"A very confused-looking genie pops out of the lamp.\" \
					} \
				} \
			]"
		)

		self.collection = EventCollection(event_inputs)

		self.assertEqual(1, len(self.collection.events))
		self.assertTrue(3001 in self.collection.events)

		event = self.collection.events[3001]
		self.assertEqual(0, event.attributes)

		match = event.match
		self.assertEqual(48, match.command_id)
		self.assertFalse(match.arguments)

		outcome = event.outcome
		self.assertEqual("A very confused-looking genie pops out of the lamp.", outcome.text)


	def test_event_with_basic_arg(self):
		event_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 3001, \
					\"attributes\": \"0\", \
					\"puzzle\": false, \
					\"match\": { \
						\"command_id\": 48, \
						\"arguments\": [ \
							{ \
								\"type\": \"item\", \
								\"value\": 1043 \
							} \
						] \
					}, \
					\"outcome\": { \
						\"text\" : \"A very confused-looking genie pops out of the lamp.\" \
					} \
				} \
			]"
		)

		self.collection = EventCollection(event_inputs)

		self.assertEqual(1, len(self.collection.events))
		event = self.collection.events[3001]
		match = event.match
		self.assertEqual(1, len(match.arguments))

		argument = match.arguments[0]
		self.assertEqual(EventMatchArgumentType.ITEM, argument.type)
		self.assertEqual(1043, argument.value)

if __name__ == "__main__":
	unittest.main()
