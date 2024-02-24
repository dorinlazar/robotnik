from roboapi import MessageHandler


class Echo(MessageHandler):
    def shortcode(self) -> str: return 'echo'
    def on_message(self, msg): return msg
