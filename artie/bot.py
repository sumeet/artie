import re
import sys
reload(sys) # So we can get back `sys.setdefaultencoding`

from twisted.internet import reactor, protocol
from twisted.python import log
from twisted.words.protocols import irc

from __init__ import VERSION
import settings
import applications
import signal

sys.setdefaultencoding('utf-8')

_user_re = re.compile(r'(.*)!(.*)@(.*)')

class NotAPrivmsg(Exception): pass

class Message(object):
	def __init__(self, user, target, message):
		try:
			self.nick, self.user, self.host = _user_re.match(user).groups()
			self.target = target
			self.text = message
		except AttributeError:
			raise NotAPrivmsg()

class Artie(irc.IRCClient):
	nickname = settings.NICK
	username = settings.USERNAME
	realname = settings.REALNAME
	versionName = 'artie for Python'
	versionNum = VERSION
	versionEnv = sys.platform

	message = None
	
	def __init__(self):
		self._reload_count = 0
		self._load_timers()
		self.channels = set()

		# SIGHUP handler to reload applications.
		def _handle_signal(signum, frame):
			self._reload_count += 1
			log.msg('Received SIGHUP. Reloading applications.')
			reload(applications)
			self._load_timers()

		signal.signal(signal.SIGHUP, _handle_signal)
	
	def signedOn(self):
		for channel in settings.CHANNELS:
			self.join(channel)
	
	def kickedFrom(self, channel, kicker, message):
		"""
		Rejoin a channel after getting kicked.
		"""
		self.join(channel)
	
	def privmsg(self, user, channel, message):
		try:
			self.message = Message(user, channel, message)
			self._trigger_match(user, channel, message)
		except NotAPrivmsg:
			return

	def joined(self, channel):
		self.channels.add(channel)

	def left(self, channel):
		try:
			self.channels.remove(channel)
		except KeyError:
			log.err('Left %s without knowing I was in there.' % channel)

	def _trigger_match(self, user, channel, message):
		for expression, func in applications.triggers:
			match = expression.match(message)
			if match:
				args = match.groups()
				kwargs = match.groupdict()
				func(self, *args, **kwargs)
	
	def _load_timers(self):
		for time, func in applications.timers:
			def _call_func():
				func(self)

			def _repeat_func(reload_count):
				if reload_count == self._reload_count:
					_call_func()
					if (time,func) in applications.timers:
						reactor.callLater(time, _repeat_func, reload_count)

			reactor.callLater(time, _repeat_func, self._reload_count)

	def reply(self, message):
		return self.msg(self.message.target, message)

class ArtieFactory(protocol.ClientFactory):
	protocol = Artie

	def __init__(self):
		self.irc = self.protocol()

	def buildProtocol(self, addr=None):
		return self.irc

	def clientConnectionLost(self, connector, reason):
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		print 'Connection failed: %s' % reason
		reactor.stop()

artie = ArtieFactory()
