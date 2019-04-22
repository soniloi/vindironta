import sys

from adventure import game

RESET_COLOUR = "\x1b[0m"
INPUT_COLOUR = "\x1b[0m"
OUTPUT_COLOUR = "\x1b[32m"
PROMPT = "> "

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print("Usage: {0} <filename>".format(sys.argv[0]))
		sys.exit(1)

	current_game = game.Game(sys.argv[1])

	while(current_game.on):
		request = input(INPUT_COLOUR + PROMPT)
		response = current_game.process_input(request).rstrip()
		if response:
			response_str = OUTPUT_COLOUR + PROMPT + response
			print(response_str)

	print(RESET_COLOUR)
