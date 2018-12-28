import json
import unittest
from unittest.mock import Mock

from adventure.event import EventMatchArgumentType, EventOutcomeActionKind, ItemEventOutcomeActionDestinationKind
from adventure.event_collection import EventCollection

class TestEventCollection(unittest.TestCase):

	def setUp(self):
		self.commands = Mock()
		self.command = Mock()
		self.commands.get.return_value = self.command

		self.items_by_id = Mock()
		self.item = Mock()
		self.items_by_id.get.return_value = self.item


	def test_event_minimal(self):
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

		self.collection = EventCollection(event_inputs, self.commands, self.items_by_id)

		self.assertEqual(1, len(self.collection.events))
		self.assertTrue((self.command,) in self.collection.events)

		event = self.collection.events[(self.command,)]
		self.assertEqual(0, event.attributes)

		match = event.match
		self.assertEqual(self.command, match.command)
		self.assertFalse(match.arguments)

		outcome = event.outcome
		self.assertEqual("A very confused-looking genie pops out of the lamp.", outcome.text)


	def test_event_with_match_args(self):
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
							}, \
							{ \
								\"type\": \"text\", \
								\"value\": \"hello\" \
							} \
						] \
					}, \
					\"outcome\": { \
						\"text\" : \"A very confused-looking genie pops out of the lamp.\" \
					} \
				} \
			]"
		)

		self.collection = EventCollection(event_inputs, self.commands, self.items_by_id)

		self.assertEqual(1, len(self.collection.events))
		self.assertTrue((self.command, self.item, "hello") in self.collection.events)

		event = self.collection.events[(self.command, self.item, "hello")]
		match = event.match
		self.assertEqual(2, len(match.arguments))

		item_argument = match.arguments[0]
		self.assertEqual(EventMatchArgumentType.ITEM, item_argument.type)
		self.assertEqual(self.item, item_argument.value)

		text_argument = match.arguments[1]
		self.assertEqual(EventMatchArgumentType.TEXT, text_argument.type)
		self.assertEqual("hello", text_argument.value)


	def test_event_with_outcome_actions(self):
		event_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 300, \
					\"attributes\": \"0\", \
					\"match\": { \
						\"command_id\": 48, \
						\"arguments\": [] \
					}, \
					\"outcome\": { \
						\"text\" : \"A very confused-looking genie pops out of the lamp.\", \
						\"actions\": [ \
							{ \
								\"kind\": \"item\", \
								\"item_id\": 1058, \
								\"destination\": { \
									\"kind\": \"destroy\" \
								} \
							}, \
							{ \
								\"kind\": \"item\", \
								\"item_id\": 1003, \
								\"destination\": { \
									\"kind\": \"replace\", \
									\"data_id\": 1050 \
								} \
							} \
						] \
					} \
				} \
			]"
		)

		self.collection = EventCollection(event_inputs, self.commands, self.items_by_id)

		self.assertEqual(1, len(self.collection.events))
		self.assertTrue((self.command,) in self.collection.events)

		event = self.collection.events[(self.command,)]
		self.assertEqual(0, event.attributes)

		match = event.match
		self.assertEqual(self.command, match.command)
		self.assertFalse(match.arguments)

		outcome = event.outcome
		self.assertEqual("A very confused-looking genie pops out of the lamp.", outcome.text)
		self.assertEqual(2, len(outcome.actions))

		first_action = outcome.actions[0]
		self.assertEqual(EventOutcomeActionKind.ITEM, first_action.kind)
		self.assertEqual(1058, first_action.item_id)
		first_action_destination = first_action.destination
		self.assertEqual(ItemEventOutcomeActionDestinationKind.DESTROY, first_action_destination.kind)
		self.assertIsNone(first_action_destination.data_id)

		second_action = outcome.actions[1]
		self.assertEqual(EventOutcomeActionKind.ITEM, second_action.kind)
		self.assertEqual(1003, second_action.item_id)
		second_action_destination = second_action.destination
		self.assertEqual(ItemEventOutcomeActionDestinationKind.REPLACE, second_action_destination.kind)
		self.assertEqual(1050, second_action_destination.data_id)


if __name__ == "__main__":
	unittest.main()
