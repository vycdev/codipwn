import os, sys
import logging

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

from flask import redirect

try:
    sys.path.append(os.path.dirname(__file__))
    from Touch_UI import Touch_Button, Touch_Screen
except Exception as e:
    logging.warn(repr(e))


def ok204_or_redirect(request):
    ua = request.user_agent
    logging.debug("UA: platform: %s, browser: %s, version: %s, language: %s\n\tstring: %s" % (ua.platform, ua.browser, ua.version, ua.language, ua.string))
    try:
        if ua.browser == 'safari':
            if ua.platform == 'iphone' or 'iPhone' in ua.string:
                logging.debug("Redirect: %s" % ua.string)
                return redirect(request.referrer)
            else:
                return 'OK', 204
        else:
            return 'OK', 204
    except Exception as e:
        logging.exception("UA: %s, error: %s" % (repr(ua), e))
        return e,204

class enable_assoc(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Enable and disable ASSOC  on the fly. Enabled when plugin loads, disabled when plugin unloads.'

    def __init__(self):
        self._agent = None
        self._count = 0
        self.hasTouch = False
        self._touchscreen = None

    # called when http://<host>:<port>/plugins/<plugin>/ is called
    # must return a html page
    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        try:
            method = request.method
            path = request.path
            if "/toggle" in path:
                self._ui._state._state['assoc_count'].state = not self._ui._state._state['assoc_count'].state
                if self._agent:
                    self._agent._config['personality']['associate'] = self._ui._state._state['assoc_count'].state
                logging.info("Toggled assoc to %s" % repr(self._ui._state._state['assoc_count'].state))
                return ok204_or_redirect(request)
            else:
                return "<html><head><title>Nothing happened</title></head><body><h1>Nothing happened.</h1></body></html>"
        except Exception as e:
            logging.exception(e)
            return "<html><head><title>Nothing happened</title></head><body><h1>Error: %s</h1></body></html>" % (e)

    # called when the plugin is loaded
    def on_loaded(self):
        self._count = 0
        pass

    # called before the plugin is unloaded
    def on_unload(self, ui):
        try:
            if not self.hasTouch and self._agent:
                self._agent._config['personality']['associate'] = False
            ui.remove_element('assoc_count')
            logging.info("[Enable_Assoc] unloading")
        except Exception as e:
            logging.warn(repr(e))

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        self._agent = agent

        self.hasTouch = self._touchscreen and self._touchscreen.running

        if self.hasTouch and self._ui:
            self._ui._state._state['assoc_count'].state = self._agent._config['personality']['associate']
        else:
            agent._config['personality']['associate'] = True

        logging.info("[Enable_Assoc] ready: enabled association")

    def on_touch_ready(self, touchscreen):
        logging.info("[ASSOC] Touchscreen %s" % repr(touchscreen))
        self._touchscreen = touchscreen
        self.hasTouch = self._touchscreen and self._touchscreen.running

    def on_touch_release(self, ts, ui, ui_element, touch_data):
        logging.debug("[ASSOC] Touch release: %s" % repr(touch_data));
        try:
            if ui_element == "assoc_count":
                logging.debug("Toggling assoc %s" % repr(self._agent._config['personality']['associate']))
                self._agent._config['personality']['associate'] = self._ui._state._state['assoc_count'].state
                logging.info("Toggled assoc to %s" % repr(self._ui._state._state['assoc_count'].state))

        except Exception as err:
            logging.info("%s" % repr(err))

    def on_touch_press(self, ts, ui, ui_element, touch_data):
        logging.debug("[ASSOC] Touch press: %s" % repr(touch_data));

    def on_association(self, agent, access_point):
        self._count += 1

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        self._ui = ui
        self.hasTouch = self._touchscreen and self._touchscreen.running
        # add custom UI elements
        if "position" in self.options:
            pos = self.options['position'].split(',')
            pos = [int(x.strip()) for x in pos]
        else:
            pos = (0,29,30,59)

        try:
            curstate = self._agent._config['personality']['associate'] if self._agent else True
            button = Touch_Button(position=pos,
                                  color='#ccccff', alt_color='White',
                                  outline="DarkGray",
                                  state=curstate,
                                  text="assoc", value=0, text_color="Black",
                                  alt_text=None, alt_text_color="Green",
                                  font=fonts.Bold, alt_font=fonts.Bold,
                                  shadow="Black", highlight="White",
                                  event_handler="enable_assoc"
                                  )
            ui.add_element('assoc_count', button)
            if hasattr(button, 'set_click_url'):
                button.set_click_url("/plugins/enable_assoc/toggle")
        except Exception as e:
            ui.add_element('assoc_count', LabeledValue(color=BLACK, label='A', value='0', position=pos,
                                                       label_font=fonts.Bold, text_font=fonts.Medium))

        # called when the ui is updated
    def on_ui_update(self, ui):
        # update those elements
        ui.set('assoc_count', '')
