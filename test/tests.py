import os
from Queue import Queue
import signal

# Make sure the tests are run from the right directory.
_tests_directory = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != _tests_directory:
    os.chdir(_tests_directory)

from twisted.internet import reactor, defer
from twisted.internet.protocol import Factory
from twisted.trial import unittest
from twisted.words.protocols import irc

from artie.bot import _user_re, ArtieFactory, settings

class TestServer(irc.IRC):
    username = None
    realname = None
    nick = None
    nickuserhost = None

    def connectionMade(self):
        def _queue_loop():
            while True:
                item = self.factory.message_queue.get()
                if item == 'end':
                    return
                else:
                    self.privmsg(*item)
        reactor.callInThread(_queue_loop)
        irc.IRC.connectionMade(self)

    def irc_USER(self, prefix, params):
        if not self.username or not self.realname:
            self.username, _, _, self.realname = params
            self._set_nickuserhost()
            self.sendMessage('001')
    
    def irc_NICK(self, prefix, params):
        self.nick = params[0]
        self._set_nickuserhost()
    
    def irc_JOIN(self, prefix, params):
        channel = params[0]
        if channel not in self.factory.channels:
            self.factory.channels[channel] = set()
        self.factory.channels[channel].add(self)
        if len(self.factory.channels) == 2:
            self.factory.on_test_ready.callback(self)

    def irc_PRIVMSG(self, prefix, params):
        target, message = params
        self.factory.sent_messages.append((self.nick, target, message))

    def _set_nickuserhost(self):
        if self.nick and self.username and self.hostname:
            nickuserhost = '%s!%s@%s' % (
                self.nick, self.username, self.hostname
            )
            if self.nickuserhost:
                self.factory.users.remove(self.nickuserhost)
            self.nickuserhost = nickuserhost
            self.factory.users.add(nickuserhost)

    def connectionLost(self, *args):
        self.factory.message_queue.put('end')
        self.factory.on_connection_lost.callback(self)

class TestArtieFactory(ArtieFactory):
    """
    Doesn't reconnect when connection is dropped.
    """
    def clientConnectionLost(self, *args):
        return

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.server = Factory()
        self.server.protocol = TestServer
        self.server.users = set()
        self.server.channels = {}
        self.server.sent_messages = [] # Format: (nick, target, message)
        self.server.message_queue = Queue()
        self.test_ready = defer.Deferred()
        self.server_disconnected = defer.Deferred()
        self.server.on_test_ready = self.test_ready
        self.server.on_connection_lost = self.server_disconnected
        self.server_port = reactor.listenTCP(7890, self.server)

        self.artie = TestArtieFactory()
        self.client_connection = reactor.connectTCP(
            settings.SERVER, 7890, self.artie
        )

        if hasattr(self, 'additional_set_up'):
            self.additional_set_up()

        return self.test_ready

    def tearDown(self):
        self.client_connection.disconnect()
        stopped = defer.maybeDeferred(self.server_port.stopListening)
        return defer.gatherResults((self.server_disconnected, stopped,))

    def assert_said(self, nick, target, message):
        self.assertTrue((nick, target, message) in self.server.sent_messages)

    def assert_not_said(self, nick, target, message):
        self.assertFalse((nick, target, message) in self.server.sent_messages)

    def msg(self, target, message):
        """
        Send a `message` to `target` from 'tests!tests@tes.t'.
        """
        self.server.message_queue.put(('tests!tests@tes.t', target, message))

class TestConnection(BaseTest):
    def test_client_connected(self):
        self.assertEqual(len(self.server.users), 1)
        nick, user, _ = _user_re.match(list(self.server.users)[0]).groups()
        self.assertEqual(nick, 'testnick')
        self.assertEqual(user, 'testuser')

    def test_client_joined_channels(self):
        self.assertEqual(len(self.server.channels), 2)
        self.assertTrue('#channel1' in self.server.channels)
        self.assertTrue('#channel2' in self.server.channels)

class TestApplication(BaseTest):
    def additional_set_up(self):
        self.msg('#channel1', '.hello test123 x')

    def test_simple_application(self):
        self.assert_said('testnick', '#channel1', 'hi test123 x')

class TestApplicationReloading(BaseTest):
    _off_file = os.path.join(settings.APPLICATION_PATH, 'sighup.py.off')
    _on_file = os.path.join(settings.APPLICATION_PATH, 'sighup.py')

    def additional_set_up(self):
        os.rename(self._off_file, self._on_file)
        signal.getsignal(signal.SIGHUP)(signal.SIGHUP, None)
        self.msg('#channel1', '.sighup test')

    def test_reloaded_application(self):
        self.assert_said('testnick', '#channel1', 'SIGHUP test')

    def tearDown(self):
        os.rename(self._on_file, self._off_file)
        signal.getsignal(signal.SIGHUP)(signal.SIGHUP, None)
        BaseTest.tearDown(self)

class TestDisabledApplications(BaseTest):
    def additional_set_up(self):
        self.msg('#channel1', '.sighup test')

    def test_disabled_application(self):
        self.assert_not_said('testnick', '#channel1', 'SIGHUP test')

if __name__ == '__main__':
    print 'Run with `trial tests`.'
