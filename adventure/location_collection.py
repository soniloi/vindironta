from adventure.direction import Direction
from adventure.element import Labels
from adventure.location import Location

class LocationCollection:

	def __init__(self, location_inputs):
		links = {}
		self.locations = self.parse_locations(location_inputs, links)
		self.cross_reference(links)


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
		return Labels(label_input["shortname"], label_input["longname"], label_input["description"])


	def parse_links(self, direction_inputs):
		links = {}
		self.parse_link(links, Direction.NORTH, direction_inputs.get("north"))
		self.parse_link(links, Direction.SOUTH, direction_inputs.get("south"))
		self.parse_link(links, Direction.EAST, direction_inputs.get("east"))
		self.parse_link(links, Direction.WEST, direction_inputs.get("west"))
		self.parse_link(links, Direction.NORTHEAST, direction_inputs.get("northeast"))
		self.parse_link(links, Direction.SOUTHWEST, direction_inputs.get("southwest"))
		self.parse_link(links, Direction.SOUTHEAST, direction_inputs.get("southeast"))
		self.parse_link(links, Direction.NORTHWEST, direction_inputs.get("northwest"))
		self.parse_link(links, Direction.UP, direction_inputs.get("up"))
		self.parse_link(links, Direction.DOWN, direction_inputs.get("down"))
		self.calculate_out(links)
		return links


	def parse_link(self, links, direction, direction_input):
		if direction_input:
			links[direction] = direction_input


	def get(self, location_id):
		return self.locations.get(location_id)


	def cross_reference(self, links):
		for location, links in links.items():
			for direction, linked_location_id in links.items():
				linked_location = self.get(linked_location_id)
				self.link(location, linked_location, direction)


	def link(self, location, linked_location, direction):
		if linked_location:
			location.directions[direction] = linked_location


	def calculate_out(self, links):
		adjacent_location_ids = set(links.values())
		if len(adjacent_location_ids) == 1:
			(out,) = adjacent_location_ids
			links[Direction.OUT] = out
