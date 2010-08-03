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
	
	def irc_NICK(self, prefix, params):
		self.nick = params[0]
		self._set_nickuserhost()

	def _set_nickuserhost(self):
		if self.nick and self.username and self.hostname:
			nickuserhost = '%s!%s@%s' % (
				self.nick, self.username, self.hostname
			)
			if self.nickuserhost:
				self.factory.users.remove(self.nickuserhost)
			self.nickuserhost = nickuserhost
			self.factory.users.add(nickuserhost)
			self.factory.onConnectionMade.callback(self)

	def connectionLost(self, *args):
		self.factory.onConnectionLost.callback(self)

class BaseTest(unittest.TestCase):
	def setUp(self):
		self.server = Factory()
		self.server.protocol = TestServer
		self.server.users = set()
		self.server_connected = defer.Deferred()
		self.server_disconnected = defer.Deferred()
		self.server.onConnectionMade = self.server_connected
		self.server.onConnectionLost = self.server_disconnected
		self.server_port = reactor.listenTCP(7890, self.server)

		artie = self.artie_factory()
		self.client_connection = reactor.connectTCP(
			settings.SERVER, 7890, artie
		)

		return self.server_connected

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

if __name__ == '__main__':
	print 'Run with `trial tests`'
