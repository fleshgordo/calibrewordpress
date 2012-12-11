#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import, print_function)
import base64
__license__   = 'GPL v3'
__copyright__ = '2012, Fresco Gamba <robot@yugo.at>'
__docformat__ = 'restructuredtext en'

from PyQt4.Qt import QWidget, QVBoxLayout, QLabel, QLineEdit

from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/interface_demo) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/wordpress_plugin')

# Set defaults
prefs.defaults['wp_url'] = 'http://www.mydomain.com'
prefs.defaults['wp_user'] = 'wp_username'
prefs.defaults['wp_password'] = 'wp_password'

prefs.defaults['draft_title'] = ''
prefs.defaults['draft_tags'] = ''
prefs.defaults['draft_post'] = ''
prefs.defaults['draft_category'] = []
prefs.defaults['draft_id'] = ''

prefs.defaults['torrenturl'] = 'http://libgen.info/search.php?search_type=magic&submit=%D0%9F%D0%BE%D0%B8%D1%81%D0%BA&search_text='
prefs.defaults['torrentview'] = 'http://libgen.info/view.php?id='

class ConfigWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
		self.setWindowTitle("Wordpress Plugin - Settings")
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.label_url = QLabel('Wordpress Host (http://yourdomain.com):')
        self.l.addWidget(self.label_url)

        self.url_msg = QLineEdit(self)
        self.url_msg.setText(prefs['wp_url'])
        self.l.addWidget(self.url_msg)
        self.label_url.setBuddy(self.url_msg)

        self.label_user = QLabel('User:')
        self.l.addWidget(self.label_user)

        self.user_msg = QLineEdit(self)
        self.user_msg.setText(prefs['wp_user'])
        self.l.addWidget(self.user_msg)
        self.label_user.setBuddy(self.user_msg)

        self.label_password = QLabel('Password:')
        self.l.addWidget(self.label_password)

        self.password_msg = QLineEdit(self)
		self.password_msg.setEchoMode(self.password_msg.Password)
		self.password_msg.setText(base64.b64decode(prefs['wp_password']))
# self.password_msg.setText(prefs['wp_password'])
        self.l.addWidget(self.password_msg)
        self.label_password.setBuddy(self.password_msg)

        self.label_torrenturl = QLabel('Torrent Search URL:')
        self.l.addWidget(self.label_torrenturl)

        self.torrenturl = QLineEdit(self)
        self.torrenturl.setText(prefs['torrenturl'])
        self.l.addWidget(self.torrenturl)

        self.label_torrentview = QLabel('Torrent View URL:')
        self.l.addWidget(self.label_torrentview)

        self.torrentview = QLineEdit(self)
        self.torrentview.setText(prefs['torrentview'])
        self.l.addWidget(self.torrentview)

    def save_settings(self):
		tmp_url = unicode(self.url_msg.text())
		tmp_url = tmp_url[-3:]
		tmp_trailing = tmp_url[-1:]
		if tmp_url == "php":
			prefs['wp_url'] = unicode(self.url_msg.text())
		elif tmp_trailing == "/":
			prefs['wp_url'] = unicode(self.url_msg.text() + "xmlrpc.php")
		else:
			prefs['wp_url'] = unicode(self.url_msg.text() + "/xmlrpc.php")
		prefs['wp_user'] = unicode(self.user_msg.text())
		# wanna store the password in plaintext??
		secret = unicode(self.password_msg.text())
		secret = base64.b64encode(secret)
		missing = 4 - len(secret) % 4
		secret += b'='* missing
		prefs['wp_password'] = secret
		prefs['torrenturl'] = unicode(self.torrenturl.text())
		prefs['torrentview'] = unicode(self.torrentview.text())
