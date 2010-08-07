from twisted.words.protocols import irc
from twisted.internet.protocol import Factory
from twisted.internet import reactor, defer
from twisted.trial import unittest
from artie.bot import settings, ArtieFactory, _user_re
from Queue import Queue
import time

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

		self.artie = self.artie_factory()
		self.client_connection = reactor.connectTCP(
			settings.SERVER, 7890, self.artie
		)

		if hasattr(self, 'additional_set_up'):
			self.additional_set_up()

		return self.test_ready

	def tearDown(self):
		self.client_connection.disconnect()
		stopped = defer.maybeDeferred(self.server_port.stopListening)
		return defer.gatherResults([self.server_disconnected, stopped,])

	def assertSaid(self, nick, target, message):
		self.assertTrue((nick, target, message) in self.server.sent_messages)
	
	def msg(self, target, message):
		"""
		Send a `message` to `target` from 'tests'.
		"""
		self.server.message_queue.put(('tests!tests@tes.t', target, message))

class TestArtieFactory(ArtieFactory):
	"""
	Doesn't reconnect when connection is dropped.
	"""
	def clientConnectionLost(self, *args):
		return

class TestConnection(BaseTest):
	artie_factory = TestArtieFactory

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
	artie_factory = TestArtieFactory

	def additional_set_up(self):
		self.msg('#channel1', '.hello test123 x')

	def test_simple_application(self):
		self.assertSaid('testnick', '#channel1', 'hi test123 x')

if __name__ == '__main__':
	print 'Run with `trial tests`.'
