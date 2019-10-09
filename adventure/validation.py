from enum import Enum

class Severity(Enum):
	ERROR = "ERROR"
	WARN = "WARN"


class Message:

	COMMAND_SHARED_ALIAS_DIFFERENT_COMMANDS = (Severity.ERROR, "Multiple commands found with alias \"{0}\". Alias will map to command {1} \"{2}\".")
	COMMAND_SHARED_ALIAS_SAME_COMMAND = (Severity.WARN, "Alias \"{0}\" given twice for command {1} \"{2}\".")
	COMMAND_SHARED_ID = (Severity.ERROR, "Multiple commands found with id {0}. Alias will map to command with primary alias \"{1}\".")
	COMMAND_TELEPORT_SHARED_SOURCES = (Severity.WARN, "Multiple destinations found for source {0} in teleport command {1} \"{2}\". Destination with id {3} will be its destination.")
	COMMAND_TELEPORT_SOURCE_DESTINATION_SAME = (Severity.WARN, "Source id and destination id {0} are the same for teleport command {1} \"{2}\".")
	COMMAND_TELEPORT_UNKNOWN_DESTINATION_ID = (Severity.ERROR, "Unknown destination location id {0} for teleport command {1} \"{2}\".")
	COMMAND_TELEPORT_UNKNOWN_SOURCE_ID = (Severity.WARN, "Unknown source location id {0} for teleport command {1} \"{2}\". This command will be unreachable.")
	COMMAND_UNRECOGNIZED_HANDLER = (Severity.WARN, "Unrecognized handler {0} for command {1} \"{2}\". This command will not be available.")
	INVENTORY_SHARED_ID = (Severity.ERROR, "Multiple inventories found with id {0}.")
	INVENTORY_MULTIPLE_DEFAULT = (Severity.ERROR, "Multiple default inventories found ({0}). Exactly one inventory must be marked as default.")
	INVENTORY_NO_DEFAULT = (Severity.ERROR, "No default inventory found. Exactly one inventory must be marked as default.")
	INVENTORY_NONE = (Severity.ERROR, "No inventories specified. At least one inventory must be given.")
	ITEM_INVALID_RELATED_COMMAND = (Severity.ERROR, "Related command id {0} given for switchable item {1} \"{2}\" does not reference a valid command.")
	ITEM_NO_SHORTNAMES = (Severity.ERROR, "No shortnames given for item with id {0}.")
	ITEM_NON_SWITCHABLE_WITH_SWITCH_INFO = (Severity.WARN, "Switch info given for non-switchable item {0} \"{1}\". This switch info will not be used.")
	ITEM_SHARED_ID = (Severity.ERROR, "Multiple items found with id {0}.")
	ITEM_SWITCHABLE_NO_RELATED_COMMAND = (Severity.ERROR, "Switchable item {0} \"{1}\" missing mandatory field \"related_command_id\".")
	ITEM_SWITCHABLE_NO_SWITCH_INFO = (Severity.ERROR, "No switch info found for switchable item {0} \"{1}\".")
	ITEM_SWITCHABLE_NON_SWITCHING_RELATED_COMMAND = (Severity.ERROR, "Switchable item {0} \"{1}\" has been specified with related command {2} \"{3}\", but this is not a switching command.")
	ITEM_WRITING_EMPTY = (Severity.WARN, "Writing given for item {0} \"{1}\" is empty. To have no writing on an item, omit the field entirely.")
	LOCATION_NO_FLOOR_NO_DOWN = (Severity.ERROR, "Location {0} has no floor, but does not specify a link in direction {1}.")
	LOCATION_NO_LAND_NO_FLOOR = (Severity.ERROR, "Location {0} has no land, but also no floor. Locations without land must have a floor.")
	LOCATION_SHARED_ID = (Severity.ERROR, "Multiple locations found with id {0}.")
	LOCATION_UNKNOWN_LINK_DESTINATION = (Severity.ERROR, "Unknown link destination {0} for direction {1} from location {2}.")
	LOCATION_UNKNOWN_LINK_DIRECTION = (Severity.ERROR, "Unknown link direction \"{0}\" from location {1}.")


	def __init__(self, error, args):
		self.severity, self.template = error
		self.args = args


	def get_formatted_message(self):
		return self.severity.value + " " + self.template.format(*self.args)
