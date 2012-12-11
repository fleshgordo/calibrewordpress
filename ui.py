#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import, print_function)
from PyQt4.Qt import QMenu, QToolButton, QUrl, QLineEdit
from calibre.gui2 import error_dialog, question_dialog, info_dialog, open_url
from calibre.gui2.actions import InterfaceAction
from calibre.utils.config import config_dir
from calibre.gui2.tag_browser.view import TagsView
from calibre_plugins.wordpress_plugin.main import PostDialog
from calibre_plugins.wordpress_plugin.utils import (set_plugin_icon_resources, get_icon, create_menu_action_unique)

__license__   = 'GPL v3'
__copyright__ = '2012, Fresco Gamba <robot@yugo.at>'
__docformat__ = 'restructuredtext en'

if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None


class WordpressPluginUI(InterfaceAction):

    name = 'Wordpress Plugin'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('Wordpress Plugin', None, 'Run the Wordpress Plugin', 'Ctrl+Shift+F1')

    def genesis(self):
        # This method is called once per plugin, do initial setup here

        # Set the icon for this interface action
        # The get_icons function is a builtin function defined for all your
        # plugin code. It loads icons from the plugin zip file. It returns
        # QIcon objects, if you want the actual data, use the analogous
        # get_resources builtin function.
        #
        # Note that if you are loading more than one icon, for performance, you
        # should pass a list of names to get_icons. In this case, get_icons
        # will return a dictionary mapping names to QIcons. Names that
        # are not found in the zip file will result in null QIcons.
        icon = get_icons('images/icon.png')

        # The qaction is automatically created from the action_spec defined
        # above
        self.qaction.setIcon(icon)
		self.menu = QMenu(self.gui)
		self.old_actions_unique_map = {}
		self.qaction.setMenu(self.menu)


    def initialization_complete(self):
        self.rebuild_menus()

    def rebuild_menus(self):
        ''' Builds the UI menus '''
        print('Rebuilding menus')
        m = self.menu
        m.clear()
        self.actions_unique_map = {}

		self.add_new_menu_item = create_menu_action_unique(self, m, _('Create/Modify Post'), None, shortcut=False, triggered=self.show_wordpress_post)
		m.addSeparator()
		self.add_new_menu_item = create_menu_action_unique(self, m, _('Settings ...'), None, shortcut=False, triggered=self.show_configuration)
#create_menu_action_unique(self, m, _('&Settings') + '...', None, shortcut=False, triggered=self.show_configuration)
        # Before we finalize, make sure we delete any actions for menus that are no longer displayed
        for menu_id, unique_name in self.old_actions_unique_map.iteritems():
            if menu_id not in self.actions_unique_map:
                self.gui.keyboard.unregister_shortcut(unique_name)
        self.old_actions_unique_map = self.actions_unique_map
        self.gui.keyboard.finalize()

        from calibre.gui2 import gprefs
        
        if self.name not in gprefs['action-layout-context-menu']:
            gprefs['action-layout-context-menu'] += (self.name, )
        if self.name not in gprefs['action-layout-toolbar']:
            gprefs['action-layout-toolbar'] += (self.name, )

        for x in (self.gui.preferences_action, self.qaction):
            x.triggered.connect(self.show_configuration)

    def create_menu_item_ex(self, parent_menu, menu_text, image=None, tooltip=None,
                           shortcut=None, triggered=None, is_checked=None, shortcut_name=None,
                           unique_name=None):
        ac = create_menu_action_unique(self, parent_menu, menu_text, image, tooltip,
                                       shortcut, triggered, is_checked, shortcut_name, unique_name)
        self.actions_unique_map[ac.calibre_shortcut_unique_name] = ac.calibre_shortcut_unique_name
        return ac

    def show_wordpress_post(self):

        # self.gui is the main calibre GUI. It acts as the gateway to access
        # all the elements of the calibre user interface, it should also be the
        # parent of the dialog
        w = PostDialog(self.gui, self.qaction.icon())
        w.show()

    def apply_settings(self):
        from calibre_plugins.wordpress_plugin.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs
    def show_configuration(self):
        print('Configuration')
        self.interface_action_base_plugin.do_user_config(self.gui)
        self.rebuild_menus()

