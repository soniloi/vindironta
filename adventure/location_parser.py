from adventure.direction import Direction
from adventure.element import Labels
from adventure.location import Location
from adventure.location_collection import LocationCollection
from adventure.validation import ValidationMessage, Severity

class LocationParser:

	TELEPORT_UNKNOWN_DESTINATION_ID = "Unknown destination location id {0} for teleport command {1} \"{2}\"."
	TELEPORT_UNKNOWN_SOURCE_ID = "Unknown source location id {0} for teleport command {1} \"{2}\". This command will be unreachable."

	def parse(self, location_inputs, teleport_infos):
		links = {}
		locations, validation = self.parse_locations(location_inputs, links)
		self.cross_reference(locations, links)

		for command, teleport_info in teleport_infos.items():
			for source_id, destination_id in teleport_info.items():
				if not source_id in locations:
					validation.append(ValidationMessage(Severity.WARN, LocationParser.TELEPORT_UNKNOWN_SOURCE_ID, (source_id, command.data_id, command.primary)))
				if not destination_id in locations:
					validation.append(ValidationMessage(Severity.ERROR, LocationParser.TELEPORT_UNKNOWN_DESTINATION_ID, (destination_id, command.data_id, command.primary)))
				else:
					destination = locations[destination_id]
					command.teleport_info[source_id] = destination

		return LocationCollection(locations), validation


	def parse_locations(self, location_inputs, links):
		locations = {}
		validation = []

		for location_input in location_inputs:
			location = self.parse_location(location_input, links)
			locations[location.data_id] = location

		return locations, validation


	def parse_location(self, location_input, links):
		location_id = location_input["data_id"]
		attributes = int(location_input["attributes"], 16)
		labels = self.parse_labels(location_input["labels"])

		location = Location(location_id, attributes, labels)
		links[location] = self.parse_links(location_input["directions"])

		return location


	def parse_labels(self, label_input):
		extended_descriptions = label_input.get("extended_descriptions", [])
		return Labels(label_input["shortname"], label_input["longname"], label_input["description"], extended_descriptions)


	def parse_links(self, direction_inputs):
		links = {}
		for direction_key_input, direction_value_input in direction_inputs.items():
			direction_key = direction_key_input.upper()
			direction = Direction[direction_key]
			self.parse_link(links, direction, direction_value_input)
		self.calculate_out(links)
		return links


	def parse_link(self, links, direction, direction_input):
		if direction_input:
			links[direction] = direction_input


	def cross_reference(self, locations, links):
		for location, links in links.items():
			for direction, linked_location_id in links.items():
				linked_location = locations.get(linked_location_id)
				self.link(location, linked_location, direction)


	def link(self, location, linked_location, direction):
		if linked_location:
			location.directions[direction] = linked_location


	def calculate_out(self, links):
		adjacent_location_ids = set(links.values())
		if len(adjacent_location_ids) == 1:
			(out,) = adjacent_location_ids
			links[Direction.OUT] = out
