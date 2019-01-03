from copy import copy
import unittest
from unittest.mock import Mock

from adventure.command import Command
from adventure.element import Labels
from adventure.event import Event, EventMatch, EventOutcome, ItemEventOutcomeAction, EventOutcomeActionKind
from adventure.event import EventMatchPrerequisiteKind, ItemEventMatchPrerequisite, ItemEventMatchPrerequisiteContainer, ItemEventMatchPrerequisiteContainerKind
from adventure.event import LocationEventMatchPrerequisite
from adventure.event import ItemEventOutcomeActionDestination, ItemEventOutcomeActionDestinationKind
from adventure.event_resolver import EventResolver
from adventure.item import Item, ContainerItem, SwitchableItem, SwitchInfo
from adventure.location import Location

class TestEventResolver(unittest.TestCase):

	def setUp(self):

		self.setup_data()
		self.setup_player()

		self.resolver = EventResolver()
		self.resolver.init_data(self.data)


	def setup_data(self):
		self.data = Mock()
		self.setup_commands()
		self.setup_locations()
		self.setup_items()

		self.data.get_item_by_id.side_effect = lambda x: {
			1003 : self.bean,
			1108 : self.bottle,
			1043 : self.lamp,
			1058 : self.potion,
			1203 : self.wand,
		}.get(x)

		self.data.get_element_by_id.side_effect = lambda x: {
			1003 : self.bean,
			1108 : self.bottle,
			1043 : self.lamp,
			1058 : self.potion,
			1203 : self.wand,
			12 : self.lighthouse_location
		}.get(x)


	def setup_commands(self):
		self.drink_command = Command(14, 0x0, [], [], "drink", {}, {})
		self.pour_command = Command(40, 0x0, [], [], "pour", {}, {})
		self.rub_command = Command(48, 0x10, [], [], ["rub"], {}, {})
		self.wave_command = Command(150, 0x0, [], [], ["wave"], {}, {})


	def setup_locations(self):
		self.lighthouse_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))


	def setup_items(self):
		self.bean = Item(1003, 0x2, Labels("bean", "a bean", "a magic bean"), 2, None)
		self.bottle = ContainerItem(1108, 0x203, Labels("bottle", "a bottle", "a small bottle"), 3, None)
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x101A, Labels("lamp", "a lamp", "a small lamp"), 2, None, lamp_switching_info)
		self.potion = Item(1058, 0x800, Labels("potion", "some potion", "some magical potion"), 1, None)
		self.wand = Item(1203, 0x2, Labels("wand", "a wand", "a magical wand"), 2, None)


	def setup_player(self):
		self.player = Mock()


	def test_resolve_event_without_match(self):
		self.data.get_event.side_effect = lambda x: {}.get(x)
		other_command = Command(1, 0x12, [], [], [""], {}, {})

		response = self.resolver.resolve_event(self.wave_command, self.player, self.wand)

		self.assertEqual((False, "", [self.wand]), response)


	def test_resolve_event_with_match_to_non_copyable_item(self):
		rub_lamp_event_match = EventMatch(command=self.rub_command, arguments=[self.lamp], prerequisites=[])
		rub_lamp_event_outcome = EventOutcome(text="A genie pops out.", actions=[])
		rub_lamp_event = Event(event_id=3001, attributes=0x0, match=rub_lamp_event_match, outcome=rub_lamp_event_outcome)
		self.data.get_event.side_effect = lambda x: {(self.rub_command, self.lamp): rub_lamp_event,}.get(x)

		response = self.resolver.resolve_event(self.rub_command, self.player, self.lamp)

		self.assertEqual((True, "A genie pops out.", [self.lamp]), response)


	def test_resolve_event_with_match_to_copyable_item(self):
		drink_potion_event_match = EventMatch(command=self.drink_command, arguments=[self.potion], prerequisites=[])
		drink_potion_event_outcome = EventOutcome(text="You become invisible.", actions=[])
		drink_potion_event = Event(event_id=3002, attributes=0x0, match=drink_potion_event_match, outcome=drink_potion_event_outcome)
		self.data.get_event.side_effect = lambda x: {(self.drink_command, self.potion): drink_potion_event,}.get(x)
		potion_copy = copy(self.potion)

		response = self.resolver.resolve_event(self.drink_command, self.player, potion_copy)

		self.assertEqual((True, "You become invisible.", [potion_copy]), response)


	def test_resolve_event_with_match_to_two_args(self):
		pour_potion_bean_event_match = EventMatch(command=self.pour_command, arguments=[self.potion, self.bean], prerequisites=[])
		destroy_bean_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.DESTROY, data_id=None)
		destroy_bean_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=destroy_bean_destination)
		pour_potion_bean_event_outcome = EventOutcome(text="The bean disappears.", actions=[destroy_bean_action])
		pour_potion_bean_event = Event(event_id=3003, attributes=0x0, match=pour_potion_bean_event_match, outcome=pour_potion_bean_event_outcome)
		self.data.get_event.side_effect = lambda x: {(self.pour_command, self.potion, self.bean): pour_potion_bean_event,}.get(x)

		response = self.resolver.resolve_event(self.pour_command, self.player, self.potion, self.bean)

		self.assertEqual((True, "The bean disappears.", [self.potion, self.bean]), response)


	# TODO: remove this test when arg list length workaround is removed
	def test_resolve_event_with_match_to_more_than_two_args(self):
		pour_potion_bean_event_match = EventMatch(command=self.pour_command, arguments=[self.potion, self.bean], prerequisites=[])
		destroy_bean_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.DESTROY, data_id=None)
		destroy_bean_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=destroy_bean_destination)
		pour_potion_bean_event_outcome = EventOutcome(text="The bean disappears.", actions=[destroy_bean_action])
		pour_potion_bean_event = Event(event_id=3003, attributes=0x0, match=pour_potion_bean_event_match, outcome=pour_potion_bean_event_outcome)
		self.data.get_event.side_effect = lambda x: {(self.pour_command, self.potion, self.bean): pour_potion_bean_event,}.get(x)

		response = self.resolver.resolve_event(self.pour_command, self.player, self.potion, self.bean, self.bottle)

		self.assertEqual((True, "The bean disappears.", [self.potion, self.bean, self.bottle]), response)


	def test_resolve_event_with_item_outcome_action_destroy(self):
		pour_potion_bean_event_match = EventMatch(command=self.pour_command, arguments=[self.potion, self.bean], prerequisites=[])
		destroy_bean_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.DESTROY, data_id=None)
		destroy_bean_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=destroy_bean_destination)
		pour_potion_bean_event_outcome = EventOutcome(text="The bean disappears.", actions=[destroy_bean_action])
		pour_potion_bean_event = Event(event_id=3003, attributes=0x0, match=pour_potion_bean_event_match, outcome=pour_potion_bean_event_outcome)
		self.data.get_event.side_effect = lambda x: {(self.pour_command, self.potion, self.bean): pour_potion_bean_event,}.get(x)
		self.lighthouse_location.add(self.bean)

		response = self.resolver.resolve_event(self.pour_command, self.player, self.potion, self.bean)

		self.assertEqual((True, "The bean disappears.", [self.potion, self.bean]), response)
		self.assertFalse(self.lighthouse_location.contains(self.bean))


	def test_resolve_event_with_item_outcome_action_current_location(self):
		wave_wand_event_match = EventMatch(command=self.wave_command, arguments=[self.wand], prerequisites=[])
		wand_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.CURRENT_LOCATION, data_id=None)
		wand_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=wand_destination)
		wave_wand_event_outcome = EventOutcome(text="The bean appears at your feet.", actions=[wand_action])
		wave_wand_event = Event(event_id=3004, attributes=0x0, match=wave_wand_event_match, outcome=wave_wand_event_outcome)
		self.data.get_event.side_effect = lambda x: {(self.wave_command, self.wand): wave_wand_event,}.get(x)

		response = self.resolver.resolve_event(self.wave_command, self.player, self.wand)

		self.assertEqual((True, "The bean appears at your feet.", [self.wand]), response)
		self.player.drop_item.assert_called_once_with(self.bean)


	def test_resolve_event_with_item_outcome_action_current_inventory(self):
		wave_wand_event_match = EventMatch(command=self.wave_command, arguments=[self.wand], prerequisites=[])
		wand_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.CURRENT_INVENTORY, data_id=None)
		wand_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=wand_destination)
		wave_wand_event_outcome = EventOutcome(text="The bean appears in your hand.", actions=[wand_action])
		wave_wand_event = Event(event_id=3005, attributes=0x0, match=wave_wand_event_match, outcome=wave_wand_event_outcome)
		self.data.get_event.side_effect = lambda x: {(self.wave_command, self.wand): wave_wand_event,}.get(x)

		response = self.resolver.resolve_event(self.wave_command, self.player, self.wand)

		self.assertEqual((True, "The bean appears in your hand.", [self.wand]), response)
		self.player.take_item.assert_called_once_with(self.bean)


	def test_resolve_event_with_item_outcome_action_absolute_container_non_copyable(self):
		wave_wand_event_match = EventMatch(command=self.wave_command, arguments=[self.wand], prerequisites=[])
		wand_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.ABSOLUTE_CONTAINER, data_id=self.lighthouse_location.data_id)
		wand_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=wand_destination)
		wave_wand_event_outcome = EventOutcome(text="The bean appears somewhere.", actions=[wand_action])
		wave_wand_event = Event(event_id=3006, attributes=0x0, match=wave_wand_event_match, outcome=wave_wand_event_outcome)
		self.data.get_event.side_effect = lambda x: {(self.wave_command, self.wand): wave_wand_event,}.get(x)

		response = self.resolver.resolve_event(self.wave_command, self.player, self.wand)

		self.assertEqual((True, "The bean appears somewhere.", [self.wand]), response)
		self.assertTrue(self.lighthouse_location.contains(self.bean))


	def test_resolve_event_with_item_outcome_action_absolute_container_copyable(self):
		wave_wand_event_match = EventMatch(command=self.wave_command, arguments=[self.wand], prerequisites=[])
		wand_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.ABSOLUTE_CONTAINER, data_id=self.bottle.data_id)
		wand_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.potion, destination=wand_destination)
		wave_wand_event_outcome = EventOutcome(text="Potion appears in the bottle.", actions=[wand_action])
		wave_wand_event = Event(event_id=3006, attributes=0x0, match=wave_wand_event_match, outcome=wave_wand_event_outcome)
		self.data.get_event.side_effect = lambda x: {(self.wave_command, self.wand): wave_wand_event}.get(x)

		response = self.resolver.resolve_event(self.wave_command, self.player, self.wand)

		self.assertEqual((True, "Potion appears in the bottle.", [self.wand]), response)
		self.assertFalse(self.bottle.contains(self.potion))
		potion_copy = self.bottle.get_allow_copy(self.potion)
		self.assertTrue(potion_copy.is_allow_copy(self.potion))


	def test_resolve_event_with_item_outcome_action_replace(self):
		wave_wand_event_match = EventMatch(command=self.wave_command, arguments=[self.wand], prerequisites=[])
		wand_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.REPLACE, data_id=self.lamp.data_id)
		wand_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=wand_destination)
		wave_wand_event_outcome = EventOutcome(text="The bean turns into a lamp.", actions=[wand_action])
		wave_wand_event = Event(event_id=3005, attributes=0x0, match=wave_wand_event_match, outcome=wave_wand_event_outcome)
		self.data.get_event.side_effect = lambda x: {(self.wave_command, self.wand): wave_wand_event,}.get(x)
		self.lighthouse_location.add(self.bean)

		response = self.resolver.resolve_event(self.wave_command, self.player, self.wand)

		self.assertEqual((True, "The bean turns into a lamp.", [self.wand]), response)
		self.assertFalse(self.lighthouse_location.contains(self.bean))
		self.assertTrue(self.lighthouse_location.contains(self.lamp))


	def test_resolve_event_with_item_any_container_prerequisite_without_match(self):
		prerequisite_kind = EventMatchPrerequisiteKind.ITEM
		prerequisite_item = self.bean
		prerequisite_container_kind = ItemEventMatchPrerequisiteContainerKind.ANY
		prerequisite_container = ItemEventMatchPrerequisiteContainer(prerequisite_container_kind, None)
		prerequisite = ItemEventMatchPrerequisite(prerequisite_kind, prerequisite_item, prerequisite_container)

		pour_potion_bean_event_match = EventMatch(command=self.pour_command, arguments=[self.potion, self.bean], prerequisites=[prerequisite])
		destroy_bean_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.DESTROY, data_id=None)
		destroy_bean_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=destroy_bean_destination)
		pour_potion_bean_event_outcome = EventOutcome(text="The bean disappears.", actions=[destroy_bean_action])
		pour_potion_bean_event = Event(event_id=3003, attributes=0x0, match=pour_potion_bean_event_match, outcome=pour_potion_bean_event_outcome)

		self.data.get_event.side_effect = lambda x: {(self.pour_command, self.potion, self.bean): pour_potion_bean_event,}.get(x)
		self.player.get_location.return_value = self.lighthouse_location

		response = self.resolver.resolve_event(self.pour_command, self.player, self.potion, self.bean)

		self.assertEqual((True, "The bean disappears.", [self.potion, self.bean]), response)
		self.assertFalse(self.lighthouse_location.contains(self.bean))


	def test_resolve_event_with_item_current_location_prerequisite_without_match(self):
		prerequisite_kind = EventMatchPrerequisiteKind.ITEM
		prerequisite_item = self.bean
		prerequisite_container_kind = ItemEventMatchPrerequisiteContainerKind.CURRENT_LOCATION
		prerequisite_container = ItemEventMatchPrerequisiteContainer(prerequisite_container_kind, None)
		prerequisite = ItemEventMatchPrerequisite(prerequisite_kind, prerequisite_item, prerequisite_container)

		pour_potion_bean_event_match = EventMatch(command=self.pour_command, arguments=[self.potion, self.bean], prerequisites=[prerequisite])
		destroy_bean_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.DESTROY, data_id=None)
		destroy_bean_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=destroy_bean_destination)
		pour_potion_bean_event_outcome = EventOutcome(text="The bean disappears.", actions=[destroy_bean_action])
		pour_potion_bean_event = Event(event_id=3003, attributes=0x0, match=pour_potion_bean_event_match, outcome=pour_potion_bean_event_outcome)

		self.data.get_event.side_effect = lambda x: {(self.pour_command, self.potion, self.bean): pour_potion_bean_event,}.get(x)
		self.player.get_location.return_value = self.lighthouse_location

		response = self.resolver.resolve_event(self.pour_command, self.player, self.potion, self.bean)

		self.assertEqual((False, "", [self.potion, self.bean]), response)
		self.assertFalse(self.lighthouse_location.contains(self.bean))


	def test_resolve_event_with_item_current_location_prerequisite_with_match(self):
		prerequisite_kind = EventMatchPrerequisiteKind.ITEM
		prerequisite_item = self.bean
		prerequisite_container_kind = ItemEventMatchPrerequisiteContainerKind.CURRENT_LOCATION
		prerequisite_container = ItemEventMatchPrerequisiteContainer(prerequisite_container_kind, None)
		prerequisite = ItemEventMatchPrerequisite(prerequisite_kind, prerequisite_item, prerequisite_container)

		pour_potion_bean_event_match = EventMatch(command=self.pour_command, arguments=[self.potion, self.bean], prerequisites=[prerequisite])
		destroy_bean_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.DESTROY, data_id=None)
		destroy_bean_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=destroy_bean_destination)
		pour_potion_bean_event_outcome = EventOutcome(text="The bean disappears.", actions=[destroy_bean_action])
		pour_potion_bean_event = Event(event_id=3003, attributes=0x0, match=pour_potion_bean_event_match, outcome=pour_potion_bean_event_outcome)

		self.data.get_event.side_effect = lambda x: {(self.pour_command, self.potion, self.bean): pour_potion_bean_event,}.get(x)
		self.player.get_location.return_value = self.lighthouse_location
		self.lighthouse_location.add(self.bean)

		response = self.resolver.resolve_event(self.pour_command, self.player, self.potion, self.bean)

		self.assertEqual((True, "The bean disappears.", [self.potion, self.bean]), response)
		self.assertFalse(self.lighthouse_location.contains(self.bean))


	def test_resolve_event_with_item_prerequisite_without_match(self):
		prerequisite_kind = EventMatchPrerequisiteKind.LOCATION
		prerequisite_location = self.lighthouse_location
		prerequisite = LocationEventMatchPrerequisite(prerequisite_kind, prerequisite_location)

		pour_potion_bean_event_match = EventMatch(command=self.pour_command, arguments=[self.potion, self.bean], prerequisites=[prerequisite])
		destroy_bean_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.DESTROY, data_id=None)
		destroy_bean_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=destroy_bean_destination)
		pour_potion_bean_event_outcome = EventOutcome(text="The bean disappears.", actions=[destroy_bean_action])
		pour_potion_bean_event = Event(event_id=3003, attributes=0x0, match=pour_potion_bean_event_match, outcome=pour_potion_bean_event_outcome)

		self.data.get_event.side_effect = lambda x: {(self.pour_command, self.potion, self.bean): pour_potion_bean_event,}.get(x)
		self.lighthouse_location.add(self.bean)

		response = self.resolver.resolve_event(self.pour_command, self.player, self.potion, self.bean)

		self.assertEqual((False, "", [self.potion, self.bean]), response)
		self.assertTrue(self.lighthouse_location.contains(self.bean))


	def test_resolve_event_with_item_prerequisite_with_match(self):
		prerequisite_kind = EventMatchPrerequisiteKind.LOCATION
		prerequisite_location = self.lighthouse_location
		prerequisite = LocationEventMatchPrerequisite(prerequisite_kind, prerequisite_location)

		pour_potion_bean_event_match = EventMatch(command=self.pour_command, arguments=[self.potion, self.bean], prerequisites=[prerequisite])
		destroy_bean_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.DESTROY, data_id=None)
		destroy_bean_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item=self.bean, destination=destroy_bean_destination)
		pour_potion_bean_event_outcome = EventOutcome(text="The bean disappears.", actions=[destroy_bean_action])
		pour_potion_bean_event = Event(event_id=3003, attributes=0x0, match=pour_potion_bean_event_match, outcome=pour_potion_bean_event_outcome)

		self.data.get_event.side_effect = lambda x: {(self.pour_command, self.potion, self.bean): pour_potion_bean_event,}.get(x)
		self.player.get_location.return_value = self.lighthouse_location
		self.lighthouse_location.add(self.bean)

		response = self.resolver.resolve_event(self.pour_command, self.player, self.potion, self.bean)

		self.assertEqual((True, "The bean disappears.", [self.potion, self.bean]), response)
		self.assertFalse(self.lighthouse_location.contains(self.bean))


	def test_resolve_event_with_item_outcome_action_current_location(self):
		wave_wand_event_match = EventMatch(command=self.wave_command, arguments=[self.wand], prerequisites=[])
		wave_wand_event_outcome = EventOutcome(text="Something happens.", actions=[])
		wave_wand_event = Event(event_id=3004, attributes=0x1, match=wave_wand_event_match, outcome=wave_wand_event_outcome)
		self.data.get_event.side_effect = lambda x: {(self.wave_command, self.wand): wave_wand_event,}.get(x)

		response = self.resolver.resolve_event(self.wave_command, self.player, self.wand)

		self.assertEqual((True, "Something happens.", [self.wand]), response)
		self.player.solve_puzzle.assert_called_once_with(3004)


if __name__ == "__main__":
	unittest.main()
