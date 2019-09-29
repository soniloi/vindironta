from enum import Enum

class Severity(Enum):
	ERROR = "ERROR"
	WARN = "WARN"


class Message:

	COMMAND_SHARED_ALIAS_DIFFERENT_COMMANDS = (Severity.ERROR, "Multiple commands found with alias \"{0}\". Alias will map to command {1} \"{2}\".")
	COMMAND_SHARED_ALIAS_SAME_COMMAND = (Severity.WARN, "Alias \"{0}\" given twice for command {1} \"{2}\".")
	COMMAND_SHARED_ID = (Severity.ERROR, "Multiple commands found with id {0}. Alias will map to command with primary alias \"{1}\".")
	COMMAND_TELEPORT_SOURCE_DESTINATION_SAME = (Severity.WARN, "Source id and destination id {0} are the same for teleport command {1} \"{2}\".")
	COMMAND_TELEPORT_UNKNOWN_DESTINATION_ID = (Severity.ERROR, "Unknown destination location id {0} for teleport command {1} \"{2}\".")
	COMMAND_TELEPORT_UNKNOWN_SOURCE_ID = (Severity.WARN, "Unknown source location id {0} for teleport command {1} \"{2}\". This command will be unreachable.")
	COMMAND_UNRECOGNIZED_HANDLER = (Severity.WARN, "Unrecognized handler {0} for command {1} \"{2}\". This command will not be available.")


	def __init__(self, error, args):
		self.severity, self.template = error
		self.args = args


	def get_formatted_message(self):
		return self.severity.value + " " + self.template.format(*self.args)
