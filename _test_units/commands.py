import cmd
import main
import asyncio
import warnings
import json
warnings.filterwarnings("ignore", category=DeprecationWarning)


class Console(cmd.Cmd):
    intro = 'Welcome to the bot console. Type help or ? to list commands.\n'
    prompt = '>>> '
    def raise_error(self,e):
        print(f"Error: {e}")

    def do_send(self, line):
        "Send specific message to every user"
        text = json.load(open('base/newsletter.json', 'r'))["text"]
        if len(text) < 1:
            raise_error("Message text must be longer than 1 symbols")
            return 0
        asyncio.get_event_loop().run_until_complete(main.newsletter_handler(text))


    def default(self, line):
        try:
            exec(line, globals())
        except Exception as e:
            print(f"Error: {e}")

    def do_exit(self, line):
        'Exit the console'
        print('Exiting the console.')
        return True

if __name__ == '__main__':
    Console().cmdloop()
