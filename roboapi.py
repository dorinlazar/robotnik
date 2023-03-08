class MessageHandler(object):
    def on_message(self, msg: str) -> str:
        print(type(self), 'does not implemented on_message')
        return ''

    def shortcode(self) -> str:
        print(type(self), 'does not implemented shortcode')
        return ''
