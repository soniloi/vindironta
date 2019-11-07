from enum import Enum

class Severity(Enum):
	ERROR = "ERROR"
	WARN = "WARN"


class Message:

	COMMAND_NON_SWITCHABLE_WITH_SWITCH_INFO = (Severity.WARN, "Command {0} \"{1}\" is not a switchable command, but switch info has been given. This switch info will be ignored.")
	COMMAND_NON_TELEPORT_WITH_TELEPORT_INFO = (Severity.WARN, "Command {0} \"{1}\" is not a teleport command, but teleport info has been given. This teleport info will be ignored.")
	COMMAND_SHARED_ALIAS_DIFFERENT_COMMANDS = (Severity.ERROR, "Multiple commands found with alias \"{0}\". Alias will map to command {1} \"{2}\".")
	COMMAND_SHARED_ALIAS_SAME_COMMAND = (Severity.WARN, "Alias \"{0}\" given twice for command {1} \"{2}\".")
	COMMAND_SHARED_ID = (Severity.ERROR, "Multiple commands found with id {0}. Alias will map to command with primary alias \"{1}\".")
	COMMAND_SMASH_MULTIPLE = (Severity.ERROR, "Multiple commands specified with the handler \"smash\". This is not supported.")
	COMMAND_SWITCHABLE_NO_SWITCH_INFO = (Severity.WARN, "Command {0} \"{1}\" is a switchable command, but no switch info has been given.")
	COMMAND_TELEPORT_NO_TELEPORT_INFO = (Severity.WARN, "Command {0} \"{1}\" is a teleport command, but no teleport info has been given. No teleports will be possible.")
	COMMAND_TELEPORT_SHARED_SOURCES = (Severity.WARN, "Multiple destinations found for source {0} in teleport command {1} \"{2}\". Destination with id {3} will be its destination.")
	COMMAND_TELEPORT_SOURCE_DESTINATION_SAME = (Severity.WARN, "Source id and destination id {0} are the same for teleport command {1} \"{2}\".")
	COMMAND_TELEPORT_UNKNOWN_DESTINATION_ID = (Severity.ERROR, "Unknown destination location id {0} for teleport command {1} \"{2}\".")
	COMMAND_TELEPORT_UNKNOWN_SOURCE_ID = (Severity.WARN, "Unknown source location id {0} for teleport command {1} \"{2}\". This command will be unreachable.")
	COMMAND_UNRECOGNIZED_HANDLER = (Severity.WARN, "Unrecognized handler {0} for command {1} \"{2}\". This command will not be available.")
	INVENTORY_DEFAULT_WITH_LOCATIONS = (Severity.WARN, "Default inventory {0} \"{1}\" has location ids specified. This is redundant.")
	INVENTORY_SHARED_ID = (Severity.ERROR, "Multiple inventories found with id {0}.")
	INVENTORY_MULTIPLE_DEFAULT = (Severity.ERROR, "Multiple default inventories found ({0}). Exactly one inventory must be marked as default.")
	INVENTORY_NO_DEFAULT = (Severity.ERROR, "No default inventory found. Exactly one inventory must be marked as default.")
	INVENTORY_NON_DEFAULT_DUPLICATE_LOCATION = (Severity.WARN, "Non-default inventory {0} \"{1}\" references location with id {2} multiple times.")
	INVENTORY_NON_DEFAULT_NO_LOCATIONS = (Severity.WARN, "Non-default inventory {0} \"{1}\" has no location ids specified. It will not be used anywhere.")
	INVENTORY_NON_DEFAULT_SHARED_LOCATION = (Severity.ERROR, "Non-default inventory {0} \"{1}\" references location with id {2}, but this location is referenced by at least one other inventory.")
	INVENTORY_NON_DEFAULT_UNKNOWN_LOCATION = (Severity.ERROR, "Non-default inventory {0} \"{1}\" references location with id {2}, but this does not reference a valid location.")
	INVENTORY_NONE = (Severity.ERROR, "No inventories specified. At least one inventory must be given.")
	ITEM_COPYABLE_NON_LIQUID = (Severity.ERROR, "Item {0} \"{1}\" has been specified as both copyable and non-liquid. This is not supported.")
	ITEM_FRAGILE_NO_SMASH_COMMAND = (Severity.ERROR, "Fragile item(s) found, but no command specified with the handler \"smash\".")
	ITEM_FRAGILE_NO_SMASH_TRANSFORMATION = (Severity.ERROR, "Item {0} \"{1}\" is fragile, but does not have a \"smash\" command replacement.")
	ITEM_INVALID_RELATED_COMMAND = (Severity.ERROR, "Related command id {0} given for switchable item {1} \"{2}\" does not reference a valid command.")
	ITEM_NO_SHORTNAMES = (Severity.ERROR, "No shortnames given for item with id {0}.")
	ITEM_NON_SWITCHABLE_WITH_SWITCH_INFO = (Severity.WARN, "Switch info given for non-switchable item {0} \"{1}\". This switch info will not be used.")
	ITEM_NON_USABLE_WITH_LIST_TEMPLATE_USING = (Severity.WARN, "Invalid list template \"using\" found for item {0} \"{1}\". This field is only valid for usable items and will be ignored here.")
	ITEM_SHARED_ID = (Severity.ERROR, "Multiple items found with id {0}.")
	ITEM_SWITCHABLE_INVALID_SWITCHED_ELEMENT = (Severity.ERROR, "Switchable item {0} \"{1}\" has invalid switched element id {2}.")
	ITEM_SWITCHABLE_NO_LIST_TEMPLATES = (Severity.WARN, "Missing or incomplete list templates found for switchable item {0} \"{1}\". While not mandatory, this will lead to incomplete descriptions of this item when listed. Switchable items should specify either \"default\" or both \"location\" and \"carrying\" list templates.")
	ITEM_SWITCHABLE_NO_RELATED_COMMAND = (Severity.ERROR, "Switchable item {0} \"{1}\" missing mandatory field \"related_command_id\".")
	ITEM_SWITCHABLE_NO_SWITCH_INFO = (Severity.ERROR, "No switch info found for switchable item {0} \"{1}\".")
	ITEM_SWITCHABLE_NON_SWITCHING_RELATED_COMMAND = (Severity.ERROR, "Switchable item {0} \"{1}\" has been specified with related command {2} \"{3}\", but this is not a switching command.")
	ITEM_TRANSFORMATION_COMMAND_UNKNOWN = (Severity.ERROR, "For item {0} \"{1}\", replacement command id {2} does not reference any known command.")
	ITEM_TRANSFORMATION_OPTIONAL_NON_ITEM = (Severity.ERROR, "For item {0} \"{1}\" with replacement command {2} \"{3}\", optional {4} element {5} \"{6}\" is not an item.")
	ITEM_TRANSFORMATION_OPTIONAL_UNKNOWN = (Severity.ERROR, "For item {0} \"{1}\" with replacement command {2} \"{3}\", optional field {4} {5} does not reference any known element.")
	ITEM_TRANSFORMATION_REPLACEMENT_NON_ITEM = (Severity.ERROR, "For item {0} \"{1}\" with replacement command {2} \"{3}\", replacement element {4} \"{5}\" is not an item.")
	ITEM_TRANSFORMATION_REPLACEMENT_NON_MOBILE = (Severity.ERROR, "For item {0} \"{1}\" with replacement command {2} \"{3}\", the replaced item is mobile but the replacement item {4} \"{5}\" is not.")
	ITEM_TRANSFORMATION_REPLACEMENT_TOO_LARGE = (Severity.ERROR, "For item {0} \"{1}\" with replacement command {2} \"{3}\", the replaced item is mobile but the replacement item {4} \"{5}\" is larger than the item being replaced.")
	ITEM_TRANSFORMATION_REPLACEMENT_UNKNOWN = (Severity.ERROR, "For item {0} \"{1}\" with replacement command {2} \"{3}\", replacement id {4} does not reference any known element.")
	ITEM_USABLE_NO_LIST_TEMPLATE_USING = (Severity.ERROR, "Mandatory list template \"using\" not found for usable item {0} \"{1}\".")
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
