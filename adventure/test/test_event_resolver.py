from copy import copy
import unittest
from unittest.mock import Mock

from adventure.command import Command
from adventure.element import Labels
from adventure.event import Event, EventMatch, EventOutcome, ItemEventOutcomeAction, EventOutcomeActionKind
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
		self.setup_events()

		self.element_by_id_map = self.item_by_id_map.copy()
		self.element_by_id_map[self.lighthouse_location.data_id] = self.lighthouse_location

		self.data.get_item_by_id.side_effect = self.item_by_id_side_effect
		self.data.get_element_by_id.side_effect = self.element_by_id_side_effect

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

		self.item_by_id_map = {
			1003 : self.bean,
			1108 : self.bottle,
			1043 : self.lamp,
			1058 : self.potion,
			1203 : self.wand,
		}


	def item_by_id_side_effect(self, *args):
		return self.item_by_id_map.get(args[0])


	def element_by_id_side_effect(self, *args):
		return self.element_by_id_map.get(args[0])


	def setup_events(self):
		self.data.get_event.side_effect = self.events_side_effect

		# Rubbing lamp prints a message
		rub_lamp_event_match = EventMatch(command=self.rub_command, arguments=[self.lamp])
		rub_lamp_event_outcome = EventOutcome(text="A genie pops out.", actions=[])
		self.rub_lamp_event = Event(event_id=3001, attributes=0x0, match=rub_lamp_event_match, outcome=rub_lamp_event_outcome)

		# Drinking potion prints a message
		drink_potion_event_match = EventMatch(command=self.drink_command, arguments=[self.potion])
		drink_potion_event_outcome = EventOutcome(text="You become invisible.", actions=[])
		self.drink_potion_event = Event(event_id=3002, attributes=0x0, match=drink_potion_event_match, outcome=drink_potion_event_outcome)

		# Pouring potion on bean causes bean to disappear
		pour_potion_bean_event_match = EventMatch(command=self.pour_command, arguments=[self.potion, self.bean])
		destroy_bean_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.DESTROY, data_id=None)
		destroy_bean_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item_id=1003, destination=destroy_bean_destination)
		pour_potion_bean_event_outcome = EventOutcome(text="The bean turns into a plant.", actions=[destroy_bean_action])
		self.pour_potion_bean_event = Event(event_id=3003, attributes=0x0, match=pour_potion_bean_event_match, outcome=pour_potion_bean_event_outcome)

		# Waving wand causes bean to appear at player's current location
		wave_wand_event_match = EventMatch(command=self.wave_command, arguments=[self.wand])
		wand_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.CURRENT_LOCATION, data_id=None)
		wand_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item_id=self.bean.data_id, destination=wand_destination)
		wave_wand_event_outcome = EventOutcome(text="The bean appears at your feet.", actions=[wand_action])
		self.wave_wand_event = Event(event_id=3004, attributes=0x0, match=wave_wand_event_match, outcome=wave_wand_event_outcome)

		# Waving lamp causes bean to appear in player's possession
		wave_lamp_event_match = EventMatch(command=self.wave_command, arguments=[self.lamp])
		lamp_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.CURRENT_INVENTORY, data_id=None)
		lamp_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item_id=self.bean.data_id, destination=lamp_destination)
		wave_lamp_event_outcome = EventOutcome(text="The bean appears in your hand.", actions=[lamp_action])
		self.wave_lamp_event = Event(event_id=3005, attributes=0x0, match=wave_lamp_event_match, outcome=wave_lamp_event_outcome)

		# Waving bottle causes lamp to appear at location
		wave_bottle_event_match = EventMatch(command=self.wave_command, arguments=[self.bottle])
		bottle_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.ABSOLUTE_CONTAINER, data_id=self.lighthouse_location.data_id)
		bottle_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item_id=self.lamp.data_id, destination=bottle_destination)
		wave_bottle_event_outcome = EventOutcome(text="A lamp appears somewhere.", actions=[bottle_action])
		self.wave_bottle_event = Event(event_id=3006, attributes=0x0, match=wave_bottle_event_match, outcome=wave_bottle_event_outcome)

		# Waving bean causes potion to be copied to bottle
		wave_bean_event_match = EventMatch(command=self.wave_command, arguments=[self.bean])
		bean_destination = ItemEventOutcomeActionDestination(kind=ItemEventOutcomeActionDestinationKind.ABSOLUTE_CONTAINER, data_id=self.bottle.data_id)
		bean_action = ItemEventOutcomeAction(kind=EventOutcomeActionKind.ITEM, item_id=self.potion.data_id, destination=bean_destination)
		wave_bean_event_outcome = EventOutcome(text="Potion appears in the bottle.", actions=[bean_action])
		self.wave_bean_event = Event(event_id=3006, attributes=0x0, match=wave_bean_event_match, outcome=wave_bean_event_outcome)

		self.event_map = {
			(self.rub_command, self.lamp): self.rub_lamp_event,
			(self.drink_command, self.potion): self.drink_potion_event,
			(self.pour_command, self.potion, self.bean): self.pour_potion_bean_event,
			(self.wave_command, self.wand): self.wave_wand_event,
			(self.wave_command, self.lamp): self.wave_lamp_event,
			(self.wave_command, self.bottle): self.wave_bottle_event,
			(self.wave_command, self.bean): self.wave_bean_event,
		}


	def events_side_effect(self, *args):
		return self.event_map.get(args[0])


	def setup_player(self):
		self.player = Mock()


	def test_resolve_event_without_match(self):
		other_command = Command(1, 0x12, [], [], [""], {}, {})

		response = self.resolver.resolve_event(other_command, self.player, "test")

		self.assertEqual((False, "", ["test"]), response)


	def test_resolve_event_with_match_to_non_copyable_item(self):
		response = self.resolver.resolve_event(self.rub_command, self.player, self.lamp)

		self.assertEqual((True, "A genie pops out.", [self.lamp]), response)


	def test_resolve_event_with_match_to_copyable_item(self):
		potion_copy = copy(self.potion)

		response = self.resolver.resolve_event(self.drink_command, self.player, potion_copy)

		self.assertEqual((True, "You become invisible.", [potion_copy]), response)


	def test_resolve_event_with_match_to_two_args(self):
		response = self.resolver.resolve_event(self.pour_command, self.player, self.potion, self.bean)

		self.assertEqual((True, "The bean turns into a plant.", [self.potion, self.bean]), response)


	# TODO: remove this test when arg list length workaround is removed
	def test_resolve_event_with_match_to_more_than_two_args(self):
		response = self.resolver.resolve_event(self.pour_command, self.player, self.potion, self.bean, self.bottle)

		self.assertEqual((True, "The bean turns into a plant.", [self.potion, self.bean, self.bottle]), response)


	def test_resolve_event_with_item_outcome_action_destroy(self):
		self.lighthouse_location.add(self.bean)

		response = self.resolver.resolve_event(self.pour_command, self.player, self.potion, self.bean)

		self.assertEqual((True, "The bean turns into a plant.", [self.potion, self.bean]), response)
		self.assertFalse(self.lighthouse_location.contains(self.bean))


	def test_resolve_event_with_item_outcome_action_current_location(self):
		response = self.resolver.resolve_event(self.wave_command, self.player, self.wand)

		self.assertEqual((True, "The bean appears at your feet.", [self.wand]), response)
		self.player.drop_item.assert_called_once_with(self.bean)


	def test_resolve_event_with_item_outcome_action_current_inventory(self):
		response = self.resolver.resolve_event(self.wave_command, self.player, self.lamp)

		self.assertEqual((True, "The bean appears in your hand.", [self.lamp]), response)
		self.player.take_item.assert_called_once_with(self.bean)


	def test_resolve_event_with_item_outcome_action_absolute_container_non_copyable(self):
		response = self.resolver.resolve_event(self.wave_command, self.player, self.bottle)

		self.assertEqual((True, "A lamp appears somewhere.", [self.bottle]), response)
		self.assertTrue(self.lighthouse_location.contains(self.lamp))


	def test_resolve_event_with_item_outcome_action_absolute_container_copyable(self):
		response = self.resolver.resolve_event(self.wave_command, self.player, self.bean)

		self.assertEqual((True, "Potion appears in the bottle.", [self.bean]), response)
		self.assertFalse(self.bottle.contains(self.potion))
		potion_copy = self.bottle.get_allow_copy(self.potion)
		self.assertTrue(potion_copy.is_allow_copy(self.potion))


if __name__ == "__main__":
	unittest.main()
