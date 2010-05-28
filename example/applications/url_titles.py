from artie.applications import trigger
from artie.helpers import work_then_callback
import urllib2
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import HTMLParser
unescape = HTMLParser.HTMLParser().unescape

def _title(url):
	# I would've just used `scrape.py`, but it doesn't get Unicode stuff
	# correct. Bummer.
	content = urllib2.urlopen(
		urllib2.Request(url, headers={"Accept" : "text/html"}),
	).read(1024*1024)
	soup = BeautifulSoup(content)
	title = unescape(
		BeautifulStoneSoup(
			soup.title.string,
			convertEntities=BeautifulStoneSoup.ALL_ENTITIES
		).contents[0].encode('utf-8')
	).strip().replace('\n', '').replace('\t', '')
	return title

@trigger(r'(.*)')
def title(irc, message):
	def _message(title):
		irc.reply('\002Link title:\002 %s' % title)

	for word in message.split(' '):
		if word.startswith('http'):
			work_then_callback(_title, _message, work_args=[word,])
