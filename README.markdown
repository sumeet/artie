# artie: IRC utility robot framework for Python

**artie** is an IRC robot that's dead simple to extend. Perfect for accessing
Internet APIs or scraping webpages.

## Installation

To install, the latest release `pip install artie` or `easy_install artie`.

For the bleeding edge, get the source from
[GitHub](http://github.com/sumeet/artie) and `python setup.py install`.

## Getting started

Make a new config file. The default name is `settings.yaml`. Follow the
example config:

    NICK: artie
    USERNAME: artie
    REALNAME: artie
    SERVER: irc.efnet.net
    PORT: 6667
    CHANNELS:
      - '#goobtown'
    APPLICATION_PATH: /home/sumeet/artiebot/applications # (Optional)

Start your bot with `artie-run.py` or `artie-run.py <configuration_file>`.

## Quick example application

To make a new application, just make a *.py* file in the `APPLICATION_PATH`.
If you don't set the application path, it'll be the `applications` directory
in the same path as your settings file.

### hello.py

    from artie.applications import trigger
    from artie.helpers import work_then_callback
    from time import sleep
    
    # Matched groups from the regular expression below get passed into the
    # decorated function.
    @trigger(r'^.hello (.*)$')
    def hello(irc, argument):
        """
        Responds back to the same channel like so:
        
        <user> .hello artie
        <artie> Hi, user. You said artie.
        """
        def _respond(text):
            irc.reply('Hi, %s. You said %s.' % (irc.message.nick, text))
        
        def _do_work(text):
            sleep(1)
            return text
        
        work_then_callback(_do_work, _respond, work_args=(argument,))

It's that easy. `work_then_callback` runs `_do_work` asynchronously and passes
the return value to `_respond`. You'll want to use `work_then_callback` like
this if you intend to use artie to access the Internet.

artie also makes it easy to do timed events:

### hello_timer.py

    from artie.applications import timer
    
    @timer(10)
    def test(irc):
        """
        Sends a message to every channel the bot is in every 10 seconds.
        """
        for channel in irc.channels:
            irc.msg(channel, 'hi i am artie')

For more examples, check out the
[sample project](http://github.com/sumeet/artie/tree/master/example/).

## Reloading applications

If you've made changes to applications or added new ones, send artie a
*SIGHUP* to reload your applications directory.
