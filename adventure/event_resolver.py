from adventure.event import EventOutcomeActionKind, ItemEventOutcomeActionDestinationKind
from adventure.item import Item
from adventure.resolver import Resolver

class EventResolver(Resolver):

	def resolve_event(self, command, player, *args):
		event = self.get_event(command, args)

		if not event:
			return False, "", list(args)

		return True, event.outcome.text, list(args)


	def get_event(self, command, args):
		event_key = self.create_event_key(command, args)
		return self.data.get_event(event_key)


	def create_event_key(self, command, args):
		event_args = self.create_event_args(args)
		# TODO: remove the list-size workaround in favour of something more robust...
		return tuple([command] + list(event_args)[:2])


	def create_event_args(self, args):
		event_args = []

		for arg in args:
			if isinstance(arg, Item):
				event_args.append(arg.get_original())
			else:
				event_args.append(arg)

		return event_args
