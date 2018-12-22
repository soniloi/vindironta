from adventure.direction import Direction
from adventure.element import Labels
from adventure.location import Location
from adventure.file_reader import FileReader


class LocationCollection:

	NO_LOCATION_ID = 0

	def __init__(self, reader):
		self.locations = {}
		links = {}

		line = reader.read_line()
		while not line.startswith("---"):
			self.create_location(line, links)
			line = reader.read_line()

		self.cross_reference(links)


	def create_location(self, line, links):
		tokens = line.split("\t")

		location_id = int(tokens[0])
		attributes = int(tokens[11], 16)
		shortname = tokens[12]
		longname = tokens[13]
		description = tokens[14]
		labels = Labels(shortname=shortname, longname=longname, description=description)

		location = Location(location_id, attributes, labels)
		self.locations[location_id] = location
		links[location] = self.parse_links(tokens)


	def parse_links(self, tokens):
		links = {}
		self.parse_link(links, Direction.NORTH, tokens[1])
		self.parse_link(links, Direction.SOUTH, tokens[2])
		self.parse_link(links, Direction.EAST, tokens[3])
		self.parse_link(links, Direction.WEST, tokens[4])
		self.parse_link(links, Direction.NORTHEAST, tokens[5])
		self.parse_link(links, Direction.SOUTHWEST, tokens[6])
		self.parse_link(links, Direction.SOUTHEAST, tokens[7])
		self.parse_link(links, Direction.NORTHWEST, tokens[8])
		self.parse_link(links, Direction.UP, tokens[9])
		self.parse_link(links, Direction.DOWN, tokens[10])
		self.calculate_out(links)
		return links


	def parse_link(self, links, direction, token):
		link_id = int(token)
		if link_id != LocationCollection.NO_LOCATION_ID:
			links[direction] = link_id


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
