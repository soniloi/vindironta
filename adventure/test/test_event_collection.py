import json
import unittest

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
					\"requirements\": { \
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

		requirements = event.requirements
		self.assertEqual(48, requirements.command_id)
		self.assertFalse(requirements.arguments)

		outcome = event.outcome
		self.assertEqual("A very confused-looking genie pops out of the lamp.", outcome.text)


if __name__ == "__main__":
	unittest.main()
