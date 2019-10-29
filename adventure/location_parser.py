from adventure.direction import Direction
from adventure.element import Labels
from adventure.location import Location
from adventure.location_collection import LocationCollection
from adventure.validation import Message, Severity

class LocationParser:

	def parse(self, location_inputs, teleport_infos):
		links = {}
		locations, validation = self.parse_locations(location_inputs, links)
		self.cross_reference(locations, links, validation)

		for command, teleport_info in teleport_infos.items():
			for source_id, destination_id in teleport_info.items():
				if not source_id in locations:
					validation.append(Message(Message.COMMAND_TELEPORT_UNKNOWN_SOURCE_ID, (source_id, command.data_id, command.primary)))
				if source_id == destination_id:
					validation.append(Message(Message.COMMAND_TELEPORT_SOURCE_DESTINATION_SAME, (source_id, command.data_id, command.primary)))
				if not destination_id in locations:
					validation.append(Message(Message.COMMAND_TELEPORT_UNKNOWN_DESTINATION_ID, (destination_id, command.data_id, command.primary)))
				else:
					destination = locations[destination_id]
					command.teleport_info[source_id] = destination

		return LocationCollection(locations), validation


	def parse_locations(self, location_inputs, links):
		locations = {}
		validation = []

		for location_input in location_inputs:
			location = self.parse_location(location_input, links, validation)

			if location.data_id in locations:
				validation.append(Message(Message.LOCATION_SHARED_ID, (location.data_id,)))
			locations[location.data_id] = location

		return locations, validation


	def parse_location(self, location_input, links, validation):
		location_id = location_input["data_id"]
		attributes = int(location_input["attributes"], 16)
		labels = self.parse_labels(location_input["labels"])

		location = Location(location_id, attributes, labels)
		links[location] = self.parse_links(location_input["directions"], validation, location_id)

		return location


	def parse_labels(self, label_input):
		extended_descriptions = label_input.get("extended_descriptions", [])
		return Labels(label_input["shortname"], label_input["longname"], label_input["description"], extended_descriptions)


	def parse_links(self, direction_inputs, validation, location_id):
		links = {}
		for direction_key_input, direction_value_input in direction_inputs.items():
			direction_key = direction_key_input.upper()
			if not direction_key in Direction.__members__:
				validation.append(Message(Message.LOCATION_UNKNOWN_LINK_DIRECTION, (direction_key_input, location_id)))
			else:
				direction = Direction[direction_key]
				links[direction] = direction_value_input
		self.calculate_out(links)
		return links


	def cross_reference(self, locations, links, validation):
		for location, links in links.items():
			for direction, linked_location_id in links.items():
				if not linked_location_id in locations:
					validation.append(Message(Message.LOCATION_UNKNOWN_LINK_DESTINATION, (linked_location_id, direction, location.data_id)))
				else:
					linked_location = locations[linked_location_id]
					location.directions[direction] = linked_location


	def calculate_out(self, links):
		adjacent_location_ids = set(links.values())
		if len(adjacent_location_ids) == 1:
			(out,) = adjacent_location_ids
			links[Direction.OUT] = out
