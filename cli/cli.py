import argparse
import sys

from adventure import data_parser

RESET_COLOUR = "\x1b[0m"
INPUT_COLOUR = "\x1b[0m"
OUTPUT_COLOUR = "\x1b[32m"
PROMPT = "> "
RESPONSE_FORMAT = OUTPUT_COLOUR + PROMPT + "{0}\n"


class Cli:

	def run(self, game, output=sys.stdout, input=sys.stdin):
		output.write(self.format_response(game.get_start_message()))

		while(game.is_running()):
			output.write(INPUT_COLOUR + PROMPT)
			output.flush()
			request = input.readline()
			response = game.process_input(request).rstrip()
			if response:
				output.write(self.format_response(response))

		output.write(RESET_COLOUR)


	def format_response(self, response):
		return RESPONSE_FORMAT.format(response)


if __name__ == '__main__':
	argparser = argparse.ArgumentParser()
	argparser.add_argument("filename", type=str, help="name of input json file defining game")
	argparser.add_argument("--validate-only", action="store_true", help="only validate the input file without running game")

	args = argparser.parse_args()
	filename = args.filename
	validate_only = args.validate_only

	current_game = data_parser.DataParser().parse(filename)

	if not validate_only:
		cli = Cli()
		cli.run(current_game)
