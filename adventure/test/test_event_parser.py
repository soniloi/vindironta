import json
import unittest

from adventure.command import Command
from adventure.direction import Direction
from adventure.element import Labels
from adventure.event import EventMatchArgumentKind, EventOutcomeActionKind, ItemEventOutcomeActionDestinationKind
from adventure.event import EventMatchPrerequisiteKind, ItemEventMatchPrerequisiteContainerKind
from adventure.event_parser import EventParser
from adventure.item import Item
from adventure.location import Location

class TestEventParser(unittest.TestCase):

	def setUp(self):
		self.setup_commands()
		self.setup_locations()
		self.setup_items()


	def setup_commands(self):
		self.command_48 = Command(48, 0x0, [], [], [""], {})
		self.command_49 = Command(49, 0x0, [], [], [""], {})
		self.commands = {
			48 : self.command_48,
			49 : self.command_49,
		}


	def setup_locations(self):
		self.lighthouse_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.beach_location = Location(13, 0x1, Labels("Beach", "on a beach", " of black sand"))
		self.locations_by_id = {
			12 : self.lighthouse_location,
			13 : self.beach_location,
		}


	def setup_items(self):
		self.book = self.book = Item(1043, 0x2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper")
		self.bread = Item(1109, 0x2, Labels("bread", "some bread", "a loaf of bread"), 2, None)
		self.items_by_id = {
			1043 : self.book,
			1044 : self.bread,
		}


	def test_parse_minimal(self):
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
						\"text_key\" : \"event_genie_lamp\" \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(1, len(collection.events))
		self.assertTrue((self.command_48,) in collection.events)

		events = collection.events[(self.command_48,)]
		self.assertEqual(1, len(events))

		event = events[0]
		self.assertEqual(0, event.attributes)

		match = event.match
		self.assertEqual(self.command_48, match.command)
		self.assertFalse(match.arguments)

		outcome = event.outcome
		self.assertEqual("event_genie_lamp", outcome.text_key)

		self.assertEqual(0, collection.puzzle_count)


	def test_parse_with_match_args(self):
		event_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 3001, \
					\"attributes\": \"0\", \
					\"match\": { \
						\"command_id\": 48, \
						\"arguments\": [ \
							{ \
								\"kind\": \"item\", \
								\"value\": 1043 \
							}, \
							{ \
								\"kind\": \"text\", \
								\"value\": \"hello\" \
							} \
						] \
					}, \
					\"outcome\": { \
						\"text_key\" : \"event_genie_lamp\" \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(1, len(collection.events))
		self.assertTrue((self.command_48, self.book, "hello") in collection.events)

		events = collection.events[(self.command_48, self.book, "hello")]
		self.assertEqual(1, len(events))

		event = events[0]
		match = event.match
		self.assertEqual(2, len(match.arguments))

		item_argument = match.arguments[0]
		self.assertEqual(EventMatchArgumentKind.ITEM, item_argument.kind)
		self.assertEqual(self.book, item_argument.value)

		text_argument = match.arguments[1]
		self.assertEqual(EventMatchArgumentKind.TEXT, text_argument.kind)
		self.assertEqual("hello", text_argument.value)

		self.assertEqual(0, collection.puzzle_count)


	def test_parse_with_item_match_prerequisites(self):
		event_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 3001, \
					\"attributes\": \"0\", \
					\"match\": { \
						\"command_id\": 48, \
						\"arguments\": [], \
						\"prerequisites\": [ \
							{ \
								\"kind\": \"item\", \
								\"data_id\": 1043, \
								\"container\": { \
									\"kind\": \"current_location\" \
								} \
							}, \
							{ \
								\"kind\": \"item\", \
								\"data_id\": 1044, \
								\"container\": { \
									\"kind\": \"absolute_container\", \
									\"container_id\": 1000 \
								} \
							} \
						] \
					}, \
					\"outcome\": { \
						\"text_key\" : \"event_genie_lamp\" \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(1, len(collection.events))
		self.assertTrue((self.command_48,) in collection.events)

		events = collection.events[(self.command_48,)]
		self.assertEqual(1, len(events))

		event = events[0]
		match = event.match

		prerequisites = match.prerequisites
		self.assertEqual(2, len(prerequisites))

		first_prerequisite = prerequisites[0]
		self.assertEqual(EventMatchPrerequisiteKind.ITEM, first_prerequisite.kind)
		self.assertEqual(self.book, first_prerequisite.item)

		first_container = first_prerequisite.container
		self.assertEqual(ItemEventMatchPrerequisiteContainerKind.CURRENT_LOCATION, first_container.kind)

		second_prerequisite = prerequisites[1]
		self.assertEqual(EventMatchPrerequisiteKind.ITEM, second_prerequisite.kind)
		self.assertEqual(self.bread, second_prerequisite.item)

		second_container = second_prerequisite.container
		self.assertEqual(ItemEventMatchPrerequisiteContainerKind.ABSOLUTE_CONTAINER, second_container.kind)

		self.assertEqual(0, collection.puzzle_count)


	def test_parse_with_location_match_prerequisites(self):
		event_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 3001, \
					\"attributes\": \"0\", \
					\"match\": { \
						\"command_id\": 48, \
						\"arguments\": [], \
						\"prerequisites\": [ \
							{ \
								\"kind\": \"location\", \
								\"data_id\": 12 \
							} \
						] \
					}, \
					\"outcome\": { \
						\"text_key\" : \"event_genie_lamp\" \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(1, len(collection.events))
		self.assertTrue((self.command_48,) in collection.events)

		events = collection.events[(self.command_48,)]
		self.assertEqual(1, len(events))

		event = events[0]
		match = event.match

		prerequisites = match.prerequisites
		self.assertEqual(1, len(prerequisites))

		prerequisite = prerequisites[0]
		self.assertEqual(EventMatchPrerequisiteKind.LOCATION, prerequisite.kind)
		self.assertEqual(self.lighthouse_location, prerequisite.location)

		self.assertEqual(0, collection.puzzle_count)


	def test_parse_with_event_match_prerequisites(self):
		event_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 3001, \
					\"attributes\": \"0\", \
					\"match\": { \
						\"command_id\": 48, \
						\"arguments\": [], \
						\"prerequisites\": [ \
							{ \
								\"kind\": \"event\", \
								\"data_id\": 3000 \
							} \
						] \
					}, \
					\"outcome\": { \
						\"text_key\" : \"event_genie_lamp\" \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(1, len(collection.events))
		self.assertTrue((self.command_48,) in collection.events)

		events = collection.events[(self.command_48,)]
		self.assertEqual(1, len(events))

		event = events[0]
		match = event.match

		prerequisites = match.prerequisites
		self.assertEqual(1, len(prerequisites))

		prerequisite = prerequisites[0]
		self.assertEqual(EventMatchPrerequisiteKind.EVENT, prerequisite.kind)
		self.assertEqual(3000, prerequisite.event_id)

		self.assertEqual(0, collection.puzzle_count)


	def test_parse_multi_event_with_different_prerequisites(self):
		event_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 3001, \
					\"attributes\": \"1\", \
					\"match\": { \
						\"command_id\": 48, \
						\"arguments\": [], \
						\"prerequisites\": [ \
							{ \
								\"kind\": \"event\", \
								\"data_id\": 3000 \
							} \
						] \
					}, \
					\"outcome\": { \
						\"text_key\" : \"event_genie_lamp\" \
					} \
				}, \
				{ \
					\"data_id\": 3002, \
					\"attributes\": \"0\", \
					\"match\": { \
						\"command_id\": 48, \
						\"arguments\": [] \
					}, \
					\"outcome\": { \
						\"text_key\" : \"event_lamp_disappear\" \
					} \
				}, \
				{ \
					\"data_id\": 3003, \
					\"attributes\": \"0\", \
					\"match\": { \
						\"command_id\": 49, \
						\"arguments\": [] \
					}, \
					\"outcome\": { \
						\"text_key\" : \"event_nothing\" \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(2, len(collection.events))
		self.assertTrue((self.command_48,) in collection.events)
		self.assertTrue((self.command_49,) in collection.events)

		events_48 = collection.events[(self.command_48,)]
		self.assertEqual(2, len(events_48))

		event_48_0 = events_48[0]
		self.assertEqual(1, event_48_0.attributes)
		match = event_48_0.match
		self.assertEqual(self.command_48, match.command)
		self.assertFalse(match.arguments)
		outcome = event_48_0.outcome
		self.assertEqual("event_genie_lamp", outcome.text_key)

		event_48_1 = events_48[1]
		self.assertEqual(0, event_48_1.attributes)
		match = event_48_1.match
		self.assertEqual(self.command_48, match.command)
		self.assertFalse(match.arguments)
		outcome = event_48_1.outcome
		self.assertEqual("event_lamp_disappear", outcome.text_key)

		events_49 = collection.events[(self.command_49,)]
		self.assertEqual(1, len(events_49))

		event_49_0 = events_49[0]
		self.assertEqual(0, event_49_0.attributes)
		match = event_49_0.match
		self.assertEqual(self.command_49, match.command)
		self.assertFalse(match.arguments)
		outcome = event_49_0.outcome
		self.assertEqual("event_nothing", outcome.text_key)

		self.assertEqual(0, collection.puzzle_count)


	def test_parse_with_item_outcome_actions(self):
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
						\"text_key\" : \"event_genie_lamp\", \
						\"actions\": [ \
							{ \
								\"kind\": \"item\", \
								\"item_id\": 1043, \
								\"destination\": { \
									\"kind\": \"destroy\" \
								} \
							}, \
							{ \
								\"kind\": \"item\", \
								\"item_id\": 1044, \
								\"destination\": { \
									\"kind\": \"replace\", \
									\"data_id\": 1044 \
								} \
							} \
						] \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(1, len(collection.events))
		self.assertTrue((self.command_48,) in collection.events)

		events = collection.events[(self.command_48,)]
		self.assertEqual(1, len(events))

		event = events[0]
		self.assertEqual(0, event.attributes)

		match = event.match
		self.assertEqual(self.command_48, match.command)
		self.assertFalse(match.arguments)

		outcome = event.outcome
		self.assertEqual("event_genie_lamp", outcome.text_key)
		self.assertEqual(2, len(outcome.actions))

		first_action = outcome.actions[0]
		self.assertEqual(EventOutcomeActionKind.ITEM, first_action.kind)
		self.assertEqual(self.book, first_action.item)
		first_action_destination = first_action.destination
		self.assertEqual(ItemEventOutcomeActionDestinationKind.DESTROY, first_action_destination.kind)
		self.assertIsNone(first_action_destination.named_data_element)

		second_action = outcome.actions[1]
		self.assertEqual(EventOutcomeActionKind.ITEM, second_action.kind)
		self.assertEqual(self.bread, second_action.item)
		second_action_destination = second_action.destination
		self.assertEqual(ItemEventOutcomeActionDestinationKind.REPLACE, second_action_destination.kind)
		self.assertEqual(self.bread, second_action_destination.named_data_element)

		self.assertEqual(0, collection.puzzle_count)


	def test_parse_with_player_outcome_actions(self):
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
						\"text_key\" : \"event_genie_lamp\", \
						\"actions\": [ \
							{ \
								\"kind\": \"player\", \
								\"attribute\": \"2\", \
								\"on\": true \
							} \
						] \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(1, len(collection.events))
		self.assertTrue((self.command_48,) in collection.events)

		events = collection.events[(self.command_48,)]
		self.assertEqual(1, len(events))

		event = events[0]
		self.assertEqual(0, event.attributes)

		match = event.match
		self.assertEqual(self.command_48, match.command)
		self.assertFalse(match.arguments)

		outcome = event.outcome
		self.assertEqual("event_genie_lamp", outcome.text_key)
		self.assertEqual(1, len(outcome.actions))

		action = outcome.actions[0]
		self.assertEqual(EventOutcomeActionKind.PLAYER, action.kind)
		self.assertEqual(2, action.attribute)
		self.assertTrue(action.on)

		self.assertEqual(0, collection.puzzle_count)


	def test_parse_with_location_outcome_actions(self):
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
						\"text_key\" : \"event_dark\", \
						\"actions\": [ \
							{ \
								\"kind\": \"location\", \
								\"location_id\": 12, \
								\"attribute\": \"1\", \
								\"on\": false \
							} \
						] \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(1, len(collection.events))
		self.assertTrue((self.command_48,) in collection.events)

		events = collection.events[(self.command_48,)]
		self.assertEqual(1, len(events))

		event = events[0]
		self.assertEqual(0, event.attributes)

		match = event.match
		self.assertEqual(self.command_48, match.command)
		self.assertFalse(match.arguments)

		outcome = event.outcome
		self.assertEqual("event_dark", outcome.text_key)
		self.assertEqual(1, len(outcome.actions))

		action = outcome.actions[0]
		self.assertEqual(EventOutcomeActionKind.LOCATION, action.kind)
		self.assertEqual(self.lighthouse_location, action.location)
		self.assertEqual(1, action.attribute)
		self.assertFalse(action.on)

		self.assertEqual(0, collection.puzzle_count)


	def test_parse_with_link_outcome_actions(self):
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
						\"text_key\" : \"event_door_move\", \
						\"actions\": [ \
							{ \
								\"kind\": \"link\", \
								\"source_id\": 12, \
								\"direction\": \"north\", \
								\"destination_id\": 13 \
							}, \
							{ \
								\"kind\": \"link\", \
								\"source_id\": 12, \
								\"direction\": \"east\" \
							} \
						] \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(1, len(collection.events))
		self.assertTrue((self.command_48,) in collection.events)

		events = collection.events[(self.command_48,)]
		self.assertEqual(1, len(events))

		event = events[0]
		self.assertEqual(0, event.attributes)

		match = event.match
		self.assertEqual(self.command_48, match.command)
		self.assertFalse(match.arguments)

		outcome = event.outcome
		self.assertEqual("event_door_move", outcome.text_key)
		self.assertEqual(2, len(outcome.actions))

		action0 = outcome.actions[0]
		self.assertEqual(EventOutcomeActionKind.LINK, action0.kind)
		self.assertEqual(self.lighthouse_location, action0.source)
		self.assertEqual(Direction.NORTH, action0.direction)
		self.assertEqual(self.beach_location, action0.destination)

		action1 = outcome.actions[1]
		self.assertEqual(EventOutcomeActionKind.LINK, action1.kind)
		self.assertEqual(self.lighthouse_location, action1.source)
		self.assertEqual(Direction.EAST, action1.direction)
		self.assertIsNone(action1.destination)

		self.assertEqual(0, collection.puzzle_count)


	def test_parse_with_description_outcome_actions(self):
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
						\"text_key\" : \"event_door_move\", \
						\"actions\": [ \
							{ \
								\"kind\": \"description\", \
								\"data_id\": 12, \
								\"extended_description_index\": 1 \
							} \
						] \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(1, len(collection.events))
		self.assertTrue((self.command_48,) in collection.events)

		events = collection.events[(self.command_48,)]
		self.assertEqual(1, len(events))

		event = events[0]
		self.assertEqual(0, event.attributes)

		match = event.match
		self.assertEqual(self.command_48, match.command)
		self.assertFalse(match.arguments)

		outcome = event.outcome
		self.assertEqual("event_door_move", outcome.text_key)
		self.assertEqual(1, len(outcome.actions))

		action = outcome.actions[0]
		self.assertEqual(EventOutcomeActionKind.DESCRIPTION, action.kind)
		self.assertEqual(self.lighthouse_location, action.named_data_element)
		self.assertEqual(1, action.extended_description_index)

		self.assertEqual(0, collection.puzzle_count)


	def test_parse_puzzle(self):
		event_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 3001, \
					\"attributes\": \"4\", \
					\"match\": { \
						\"command_id\": 48, \
						\"arguments\": [] \
					}, \
					\"outcome\": { \
						\"text_key\" : \"event_genie_lamp\" \
					} \
				} \
			]"
		)

		collection = EventParser().parse(event_inputs, self.commands, self.items_by_id, self.locations_by_id)

		self.assertEqual(1, len(collection.events))
		self.assertTrue((self.command_48,) in collection.events)

		events = collection.events[(self.command_48,)]
		self.assertEqual(1, len(events))

		event = events[0]
		self.assertEqual(4, event.attributes)

		match = event.match
		self.assertEqual(self.command_48, match.command)
		self.assertFalse(match.arguments)

		outcome = event.outcome
		self.assertEqual("event_genie_lamp", outcome.text_key)

		self.assertEqual(1, collection.puzzle_count)


if __name__ == "__main__":
	unittest.main()
