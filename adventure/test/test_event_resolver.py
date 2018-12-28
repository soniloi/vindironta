from copy import copy
import unittest
from unittest.mock import Mock

from adventure.command import Command
from adventure.element import Labels
from adventure.event import Event, EventMatch, EventOutcome
from adventure.event_resolver import EventResolver
from adventure.item import Item, ContainerItem, SwitchableItem, SwitchInfo

class TestEventResolver(unittest.TestCase):

	def setUp(self):

		self.setup_data()
		self.setup_player()

		self.resolver = EventResolver()
		self.resolver.init_data(self.data)


	def setup_data(self):
		self.data = Mock()
		self.setup_commands()
		self.setup_items()
		self.setup_events()


	def setup_commands(self):
		self.drink_command = Command(14, 0x0, [], [], "drink", {}, {})
		self.pour_command = Command(40, 0x0, [], [], "pour", {}, {})
		self.rub_command = Command(48, 0x10, [], [], ["rub"], {}, {})


	def setup_items(self):
		self.bean = Item(1003, 0x2, Labels("bean", "a bean", "a magic bean"), 2, None)
		self.bottle = ContainerItem(1108, 0x203, Labels("bottle", "a bottle", "a small bottle"), 3, None)
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x101A, Labels("lamp", "a lamp", "a small lamp"), 2, None, lamp_switching_info)
		self.potion = Item(1058, 0x800, Labels("potion", "some potion", "some magical potion"), 1, None)


	def setup_events(self):
		self.data.get_event.side_effect = self.events_side_effect

		drink_potion_event_match = EventMatch(command=self.drink_command, arguments=[self.potion])
		drink_potion_event_outcome = EventOutcome(text="You become invisible.", actions=[])
		self.drink_potion_event = Event(event_id=3002, attributes=0x0, match=drink_potion_event_match, outcome=drink_potion_event_outcome)

		pour_potion_bean_event_match = EventMatch(command=self.pour_command, arguments=[self.potion, self.bean])
		pour_potion_bean_event_outcome = EventOutcome(text="The bean turns into a plant.", actions=[])
		self.pour_potion_bean_event = Event(event_id=3003, attributes=0x0, match=pour_potion_bean_event_match, outcome=pour_potion_bean_event_outcome)

		rub_lamp_event_match = EventMatch(command=self.rub_command, arguments=[self.lamp])
		rub_lamp_event_outcome = EventOutcome(text="A genie pops out.", actions=[])
		self.rub_lamp_event = Event(event_id=3001, attributes=0x0, match=rub_lamp_event_match, outcome=rub_lamp_event_outcome)

		self.event_map = {
			(self.drink_command, self.potion): self.drink_potion_event,
			(self.pour_command, self.potion, self.bean): self.pour_potion_bean_event,
			(self.rub_command, self.lamp): self.rub_lamp_event,
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


if __name__ == "__main__":
	unittest.main()
