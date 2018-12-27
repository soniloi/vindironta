import unittest
from unittest.mock import Mock

from adventure.command import Command
from adventure.element import Labels
from adventure.event import Event, EventMatch, EventOutcome
from adventure.event_resolver import EventResolver
from adventure.item import Item, SwitchableItem, SwitchInfo

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
		self.rub_command = Command(48, 0x10, [], [], ["rub"], {}, {})


	def setup_items(self):
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x101A, Labels("lamp", "a lamp", "a small lamp"), 2, None, lamp_switching_info)


	def setup_events(self):
		self.data.get_event.side_effect = self.events_side_effect

		rub_lamp_event_match = EventMatch(self.rub_command, [self.lamp])
		rub_lamp_event_outcome = EventOutcome(text="A genie pops out.")
		self.rub_lamp_event = Event(event_id=3001, attributes=0x0, match=rub_lamp_event_match, outcome=rub_lamp_event_outcome)

		self.event_map = {
			(self.rub_command, self.lamp): self.rub_lamp_event
		}


	def events_side_effect(self, *args):
		return self.event_map.get(args[0])


	def setup_player(self):
		self.player = Mock()


	def test_resolve_event_without_match(self):
		other_command = Command(1, 0x12, [], [], [""], {}, {})

		response = self.resolver.resolve_event(other_command, self.player, "test")

		self.assertEqual((False, "", ["test"]), response)


	def test_resolve_event_with_match(self):
		response = self.resolver.resolve_event(self.rub_command, self.player, self.lamp)

		self.assertEqual((True, "A genie pops out.", [self.lamp]), response)


if __name__ == "__main__":
	unittest.main()
