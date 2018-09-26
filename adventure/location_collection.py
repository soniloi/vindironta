from adventure.direction import Direction
from adventure.location import Location
from adventure.file_reader import FileReader


class LocationCollection:

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
		location_links[location] = self.create_links(tokens)


	def create_links(self, tokens):
		links = {}
		links[Direction.NORTH] = int(tokens[1])
		links[Direction.SOUTH] = int(tokens[2])
		links[Direction.EAST] = int(tokens[3])
		links[Direction.WEST] = int(tokens[4])
		links[Direction.NORTHEAST] = int(tokens[5])
		links[Direction.SOUTHWEST] = int(tokens[6])
		links[Direction.SOUTHEAST] = int(tokens[7])
		links[Direction.NORTHWEST] = int(tokens[8])
		links[Direction.UP] = int(tokens[9])
		links[Direction.DOWN] = int(tokens[10])
		# TODO: maybe rethink how this works
		links[Direction.BACK] = Location.NO_LOCATION_ID
		return links


	def get(self, location_id):
		if location_id in self.locations:
			return self.locations[location_id]
		return None


	def cross_reference(self, location_links):
		for location, links in location_links.items():
			for _, member in Direction.__members__.items():
				location.directions[member] = self.get(links[member])
