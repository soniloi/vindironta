from adventure.direction import Direction
from adventure.element import Labels
from adventure.location import Location
from adventure.location_collection import LocationCollection

class LocationParser:

	def parse(self, location_inputs, teleport_infos):
		links = {}
		locations = self.parse_locations(location_inputs, links)
		self.cross_reference(locations, links)

		for command, teleport_info in teleport_infos.items():
			for source_id, destination_id in teleport_info.items():
				destination = locations[destination_id]
				command.teleport_info[source_id] = destination

		return LocationCollection(locations)


	def parse_locations(self, location_inputs, links):
		locations = {}

		for location_input in location_inputs:
			location = self.parse_location(location_input, links)
			locations[location.data_id] = location

		return locations


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
