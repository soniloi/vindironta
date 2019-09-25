from enum import Enum

class Severity(Enum):
	ERROR = "ERROR"
	WARN = "WARN"


class ValidationMessage:

	def __init__(self, severity, template, args):
		self.severity = severity
		self.template = template
		self.args = args


	def get_formatted_message(self):
		return self.severity.value + " " + self.template.format(*self.args)
