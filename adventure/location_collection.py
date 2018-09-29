from adventure.direction import Direction
from adventure.location import Location
from adventure.file_reader import FileReader


class LocationCollection:

	NO_LOCATION_ID = 0

	def __init__(self, reader):
		self.locations = {}
		location_links = {}

		line = reader.read_line()
		while not line.startswith("---"):
			self.create_location(line, location_links)
			line = reader.read_line()

		self.cross_reference(location_links)


	def create_location(self, line, location_links):
		tokens = line.split("\t")

		location_id = int(tokens[0])
		location_attributes = int(tokens[11], 16)
		location_shortname = tokens[12]
		location_longname = tokens[13]
		location_description = tokens[14]

		location = Location(location_id, location_attributes, location_shortname, location_longname,
			location_description)
		self.locations[location_id] = location
		location_links[location] = self.parse_links(tokens)


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


	def cross_reference(self, location_links):
		for location, links in location_links.items():
			for direction, linked_location_id in links.items():
				linked_location = self.get(linked_location_id)
				self.link(location, linked_location, direction)


	def link(self, location, linked_location, direction):
		if linked_location:
			location.directions[direction] = linked_location


	def calculate_out(self, location_links):
		adjacent_location_ids = set(location_links.values())
		if len(adjacent_location_ids) == 1:
			(out,) = adjacent_location_ids
			location_links[Direction.OUT] = out
