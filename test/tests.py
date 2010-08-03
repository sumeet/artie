from twisted.words.protocols import irc
from twisted.internet.protocol import Factory
from twisted.internet import reactor, defer
from twisted.trial import unittest
from artie.bot import settings, ArtieFactory, _user_re

class TestServer(irc.IRC):
	username = None
	realname = None
	nick = None
	nickuserhost = None
	
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
		self.factory.on_connection_lost.callback(self)

class BaseTest(unittest.TestCase):
	def setUp(self):
		self.server = Factory()
		self.server.protocol = TestServer
		self.server.users = set()
		self.server.channels = {}
		self.test_ready = defer.Deferred()
		self.server_disconnected = defer.Deferred()
		self.server.on_test_ready = self.test_ready
		self.server.on_connection_lost = self.server_disconnected
		self.server_port = reactor.listenTCP(7890, self.server)

		self.artie = self.artie_factory()
		self.client_connection = reactor.connectTCP(
			settings.SERVER, 7890, self.artie
		)

		return self.test_ready

	def tearDown(self):
		self.client_connection.disconnect()
		stopped = defer.maybeDeferred(self.server_port.stopListening)
		return defer.gatherResults([self.server_disconnected, stopped,])

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
		self.assertEqual(nick, 'nick')
		self.assertEqual(user, 'user')

	def test_client_joined_channels(self):
		self.assertEqual(len(self.server.channels), 2)
		self.assertTrue('#channel1' in self.server.channels)
		self.assertTrue('#channel2' in self.server.channels)

if __name__ == '__main__':
	reactor.listenTCP(7890, _create_server_factory())
	reactor.run()
