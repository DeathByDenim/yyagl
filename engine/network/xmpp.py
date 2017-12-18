import logging
try:
    from sleekxmpp import ClientXMPP
except ImportError:  # sleekxmpp requires openssl 1.0.2
    print 'OpenSSL 1.0.2 not detected'
    class ClientXMPP:
        def __init__(self, jid, password): pass


class XMPP(object):

    def __init__(self):
        self.xmpp = None

    def start(self, usr, pwd, on_ok, on_fail):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(levelname)-8s %(message)s')
        self.xmpp = EchoBot(usr, pwd, on_ok, on_fail)
        if self.xmpp.connect(): self.xmpp.process()

    def destroy(self):
        if self.xmpp: self.xmpp.disconnect()
        self.xmpp = None


class EchoBot(ClientXMPP):

    def __init__(self, jid, password, on_ok, on_ko):
        ClientXMPP.__init__(self, jid, password)
        self.on_ok = on_ok
        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('message', self.message)
        self.add_event_handler('failed_auth', on_ko)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        self.on_ok()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()
