#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__   = 'GPL v3'
__copyright__ = '2012, Fresco Gamba <bled@bled.si>'
__docformat__ = 'restructuredtext en'

if False:
    get_icons = get_resources = None

from PyQt4.Qt import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QLabel, QLineEdit, QRadioButton, QTextEdit, QColor, QCheckBox, QButtonGroup, QSize, QProgressBar
from calibre.ebooks.metadata.sources.base import (get_cached_cover_urls, msprefs)
from calibre.utils.formatter_functions import (BuiltinHasCover)
from calibre_plugins.wordpress_plugin.wordpresslib import *
from calibre_plugins.wordpress_plugin.urllib import urlopen
import base64,time

from calibre_plugins.wordpress_plugin.config import prefs

class PostDialog(QDialog):
    def __init__(self, gui, icon):
        QDialog.__init__(self, gui)
		self.setWindowTitle("Wordpress Plugin - Create new post")
#		self.resize(900,700)
        self.gui = gui
        self.db = gui.current_db

		rows = self.gui.library_view.selectionModel().selectedRows()
		for row in rows:
			self.calibre_id = self.db.id(row.row())
			self.mi = self.db.get_metadata(self.calibre_id, index_is_id=True)
			self.book_has_cover = False
			if self.db.has_cover(self.calibre_id):
				self.book_has_cover = True
				self.path_to_cover = os.path.join(self.db.library_path, self.db.path(self.calibre_id, index_is_id=True), 'cover.jpg')
#				print (self.mi)
		self.l = QVBoxLayout()

		self.label_post_title = QLabel('Post title:')
		self.l.addWidget(self.label_post_title)

		self.msg_post_title = QLineEdit(self)
		self.msg_post_title.setText(self.mi.title)
		self.l.addWidget(self.msg_post_title)
		self.label_post_title.setBuddy(self.msg_post_title)

		if self.book_has_cover == True:
			self.msg_post_image = QCheckBox(self)
			self.msg_post_image.setText("Add cover image to post")
			self.l.addWidget(self.msg_post_image)
			self.msg_post_image.toggled.connect(self.add_image)

		self.label_post_title.setBuddy(self.msg_post_title)

		try:
			self.label_post_category = QLabel('Categories:')
			self.l.addWidget(self.label_post_category)
			self.get_category()
		except WordPressException:
			self.error_dialog("Can't connect to Wordpress! Check URL, user in settings again! Some features might not work properly!")
			self.label_post_category = QLabel('No Categories available')
			self.l.addWidget(self.label_post_category)
			self.close()

		self.label_post_content = QLabel('Post Content:')
		self.l.addWidget(self.label_post_content)

		self.msg_post_content = QTextEdit(self)
		try:
			self.msg_post_content.setHtml(self.mi.comments)
		except:
			pass
		self.l.addWidget(self.msg_post_content)

		self.h = QHBoxLayout()
		self.torrent_button = QPushButton('Add Torrent-Link to post', self)
		self.torrent_button.setMaximumSize(QSize(220,30))
		self.torrent_button.clicked.connect(self.get_torrent)
		self.h.addWidget(self.torrent_button)

		self.draft_button = QPushButton('Save Draft locally', self)
		self.draft_button.setMaximumSize(QSize(150,30))
		self.draft_button.clicked.connect(self.save_draft)
		self.h.addWidget(self.draft_button)

		self.draft_online_button = QPushButton('Save Draft online', self)
		self.draft_online_button.setMaximumSize(QSize(150,30))
		self.draft_online_button.clicked.connect(lambda arg=False: self.create_post(arg))
		self.h.addWidget(self.draft_online_button)

		self.post_button = QPushButton('Publish', self)
		self.post_button.clicked.connect(lambda arg=True: self.create_post(arg))
		self.h.addWidget(self.post_button)

		self.l.addLayout(self.h)

		self.setLayout(self.l)

		if self.calibre_id == prefs['draft_id']:
			try:
				self.recover_draft()
			except:
				pass
	

	def create_category_list(self):
		categorylist = []
		for key,value in self.categories.iteritems():
			if (value.isChecked() == True):
				categorylist.append(self.category_group.id(value))
		return categorylist

	def create_post(self,published):
		self.wp = self.connect()
		if self.wp !=0:
			self.post = WordPressPost()
			self.post.title = str(self.msg_post_title.text())
			self.post.description = str(self.msg_post_content.toPlainText())
			self.post.categories = self.create_category_list()
			if published == True:
				returnid = self.wp.newPost(self.post, published)
			else:
				returnid = self.wp.newPost(self.post, published)
			if returnid != 0:
				self.error_dialog("Successfully posted to Wordpress!")
				self.save_draft
				self.close()
				return 1
		else:
			self.error_dialog("Can't connect to Wordpress! Check URL, user in settings again!")

	def add_image(self):
        if self.msg_post_image.isChecked() == True:
			if self.book_has_cover == True:
				self.msg_post_image_upload = True
				self.wp = self.connect()
				self.img_url = self.wp.newMediaObject(self.path_to_cover)
				url_embed = "<img src=\"" + self.img_url + "\" />"
				self.msg_post_content.insertPlainText (url_embed)
		else:
			self.msg_post_content.undo()
			
	def connect(self):
		wp = WordPressClient(prefs["wp_url"], prefs["wp_user"], base64.b64decode(prefs["wp_password"]))
		return wp

	def error_dialog(self,error_message):
		self.q = QDialog(self)
		self.q.setWindowTitle("Dialog")
		self.q.l = QVBoxLayout()
		self.q.setLayout(self.q.l)

		self.connection_title = QLabel(error_message)
		self.q.l.addWidget(self.connection_title)
		self.q.ok_button = QPushButton('OK', self)
		self.q.ok_button.clicked.connect(self.close_dialog)
		self.q.l.addWidget(self.q.ok_button)
		self.q.exec_()

	def close_dialog(self):
		self.q.close()

	def get_category(self):
		self.wp = self.connect()
		if self.wp !=0:
			self.msg_categories = self.wp.getCategoryList()
			self.categories = {}
			# create buttongroup and set multiple checkboxes
			self.category_group = QButtonGroup()
			self.category_group.setExclusive(False)
			# dict for button objects and category IDs
			for cat in self.msg_categories:
				self.categories[cat.id] = QCheckBox(cat.name,self)
			# add button to dialog layout
			for key,value in self.categories.iteritems():
				self.category_group.addButton(value,key)
				self.l.addWidget(value)
		else:
			self.msg_categories = ""
			
	def get_torrent(self):
		self.t = QDialog(self)
		self.t.setWindowTitle("Add torrent link to post")
        self.t.l = QVBoxLayout()
        self.t.setLayout(self.t.l)
		self.t.show()
		self.t.label_torrent_looking = QLabel('Looking for torrents...')
		self.t.l.addWidget(self.t.label_torrent_looking)
		self.t.label_torrent_looking.show()
		self.t.label_torrent_looking.repaint()
		self.t.progress = QProgressBar()
		self.t.progress.setMinimum(0)
		self.t.progress.setMaximum(100)
		self.t.l.addWidget(self.t.progress)
		self.t.progress.show()
		self.t.progress.setValue(33)
		self.t.progress.repaint()
		time.sleep(0.2)
		try:
			self.query_libgen_url = prefs['torrenturl'] + str(self.mi.title)
			self.t.progress.setValue(66)
			self.t.progress.repaint()
			filehandle = urlopen(self.query_libgen_url)
			websource = filehandle.read()
			libgen_ids = re.findall(r'id=(\d*?)"', str(websource)) 
			libgen_titles = re.findall(r'id=\d*?","_self"\)\'>(.*?)</a>', str(websource))

			libgen_ids = filter(None, libgen_ids)
			self.results = {}
			for j,ids in enumerate(libgen_ids):
				self.results[ids] = libgen_titles[j]
			
			print(self.results)
			if len(self.results.items()) == 0:
				raise NameError()

			self.t.label_torrent_title = QLabel('Torrent(s):')
			self.t.l.addWidget(self.t.label_torrent_title)
			self.t.progress.setValue(99)
			self.t.progress.repaint()
			# create buttongroup and set multiple checkboxes
			self.t.torrent_group = QButtonGroup()
			self.t.torrent_group.setExclusive(True)
			self.resultsbuttons = {}
			for libgen_id,libgen_title in self.results.iteritems():
				self.resultsbuttons[libgen_id] = QRadioButton(libgen_title,self.t)
			# add button to dialog layout
			for libgen_id, libgen_button in self.resultsbuttons.iteritems():
				self.t.torrent_group.addButton(libgen_button,int(libgen_id))
				self.t.l.addWidget(libgen_button)
			self.t.submit_torrent = QPushButton('Add Torrent to Post')
			self.t.submit_torrent.clicked.connect(self.return_torrent)
			self.t.l.addWidget(self.t.submit_torrent)
			self.t.progress.setValue(100)
			self.t.progress.hide()
			self.t.label_torrent_looking.hide()

		except NameError, TypeError:
			self.t.progress.hide()
			self.t.label_torrent_looking.hide()
			self.t.label_torrent_title = QLabel('Sorry, no torrents available!')
			self.t.l.addWidget(self.t.label_torrent_title)
			self.t.exec_()
			pass

	def return_torrent(self):
		self.selected_torrent = self.t.torrent_group.checkedId()
		self.selected_torrent_url = "<a href=\"" + prefs['torrentview'] + str(self.selected_torrent) + "\" target=\"_blank\">Download</a> "
		self.msg_post_content.insertPlainText(self.selected_torrent_url)
		self.t.done(1)
		
	def recover_draft(self):
		recover_categories = prefs['draft_category']
		for recover_cat in recover_categories:
			if self.categories.has_key(recover_cat) == True:
				self.categories[recover_cat].setChecked(True)
		self.msg_post_content.setHtml(prefs['draft_post'])
		self.msg_post_title.setText(prefs['draft_title'])

	def save_draft(self):
		prefs['draft_post'] = unicode(self.msg_post_content.toPlainText())
		prefs['draft_title'] = unicode(self.msg_post_title.text())
		try:
			prefs['draft_category'] = self.create_category_list()
		except:
			prefs['draft_category'] = "" 
		prefs['draft_id'] = self.calibre_id
