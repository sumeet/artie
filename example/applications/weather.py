from artie.applications import trigger
from artie.helpers import work_then_callback

from scrape import s
from urllib import urlencode

API_URL = \
'http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?%s'

def _weather(query):
	weather_url = API_URL % urlencode({'query': query})
	try:
		s.go(weather_url)
		current = s.doc.first('current_observation')
		return {
			'location': current.first('display_location').first('full').text,
			'temperature': current.first('temperature_string').text,
			'condition': current.first('weather').text,
			'heat_index': current.first('heat_index_string').text,
			'windchill': current.first('windchill_string').text
		}
	except:
		pass

@trigger(r'^.wz (.*)$')
def weather(irc, query):
	"""
	Tells the weather. Example:

	<user> .wz 45440
	<artie> Weather for Dayton, OH: 83 F (28 C) Partly Cloudy
	"""
	def _message(weather):
		if not weather:
			irc.reply(
				'Error while looking up weather for \002%s\002.' % query
			)
			return

		if len(weather.get('location', '')) < 2:
			irc.reply('Weather for \002%s\002 not found.' % query)
			return

		feels_like = (
			weather.get('heat_index') if weather.get('heat_index') != 'NA'
			else weather.get('windchill') if weather.get('windchill') != 'NA'
			else None
		)

		location = weather.get('location')
		temperature = weather.get('temperature')
		condition = weather.get('condition')

		if condition:
			condition = condition.title()


		if feels_like:
			condition += ' (Feels like %s)' % feels_like

		irc.reply(
			'Weather for \002%s\002: %s %s' % (
				location, temperature, condition
			)
		)	

	work_then_callback(_weather, _message, work_args=[query,])
