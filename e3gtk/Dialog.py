# -*- coding: utf-8 -*-

#   This file is part of emesene.
#
#    Emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    emesene is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with emesene; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''a module that defines the api of objects that display dialogs'''

import gtk
import pango

import gui
import utils
import stock
import protocol
import extension

import ContactInformation
from debugger import dbg

# TODO: remove this
_ = lambda x: x

class Dialog(object):
    '''a class full of static methods to handle dialogs, dont instantiate it'''
    NAME = 'Dialog'
    DESCRIPTION = 'Class to show all the dialogs of the application'
    AUTHOR = 'Mariano Guerra'
    WEBSITE = 'www.emesene.org'

    @classmethod
    def window_add_image(cls, window, stock_id):
        '''add a stock image as the first element of the window.hbox'''

        image = gtk.image_new_from_stock(stock_id, gtk.ICON_SIZE_DIALOG)
        window.hbox.pack_start(image, False)
        image.show()

        return image

    @classmethod
    def window_add_button(cls, window, stock_id, label=''):
        '''add a button to the window'''

        button = gtk.Button(label, stock=stock_id)
        window.bbox.pack_start(button, True, True)
        button.show()

        return button

    @classmethod
    def window_add_label(cls, window, text):
        '''add a label with the text (as pango) on the window'''

        label = gtk.Label()
        #label.set_selectable(True)
        label.set_use_markup(True)
        label.set_markup('<span>' + \
            text + "</span>")
        window.hbox.pack_start(label, True, True)
        label.show()

        return label

    @classmethod
    def close_cb(cls, widget, event, window, response_cb, *args):
        '''default close callback, call response_cb with args if it's not
        None'''

        if response_cb:
            response_cb(*args)

        window.hide()

    @classmethod
    def default_cb(cls, widget, window, response_cb, *args):
        '''default callbacks, call response_cb with args if it's not
        None'''

        if response_cb:
            response_cb(*args)

        window.hide()

    @classmethod
    def entry_cb(cls, widget, window, response_cb, *args):
        '''callback called when the entry is activated, it call the response
        callback with the stock.ACCEPT and append the value of the entry
        to args'''
        args = list(args)
        args.append(window.entry.get_text())

        if response_cb:
            if type(widget) == gtk.Entry:
                response_cb(stock.ACCEPT, *args)
            else:
                response_cb(*args)

        window.hide()

    @classmethod
    def add_contact_cb(cls, widget, window, response_cb, response):
        '''callback called when a button is selected on the add_contact 
        dialog'''
        contact = window.entry.get_text()
        group = window.combo.get_model().get_value(
            window.combo.get_active_iter(), 0)

        window.hide()
        response_cb(response, contact, group)

    @classmethod
    def common_window(cls, message, stock_id, response_cb, title):
        '''create a window that displays a message with a stock image'''
        window = cls.new_window(title, response_cb)
        cls.window_add_image(window, stock_id)
        cls.window_add_label(window, message)

        return window

    @classmethod
    def message_window(cls, message, stock_id, response_cb, title):
        '''create a window that displays a message with a stock image
        and a close button'''
        window = cls.common_window(message, stock_id, response_cb, title)
        cls.add_button(window, gtk.STOCK_CLOSE, stock.CLOSE, response_cb,
            cls.default_cb)

        return window

    @classmethod
    def entry_window(cls, message, text, response_cb, title, *args):
        '''create a window that contains a label and a entry with text set
        and selected, and two buttons, accept, cancel'''
        window = cls.new_window(title, response_cb)
        cls.window_add_label(window, message)

        entry = gtk.Entry()
        entry.set_text(text)
        entry.select_region(0, -1)

        entry.connect('activate', cls.entry_cb, window, response_cb, *args)

        window.hbox.pack_start(entry, True, True)
        cls.add_button(window, gtk.STOCK_CANCEL, stock.CANCEL, response_cb, 
            cls.entry_cb, *args)
        cls.add_button(window, gtk.STOCK_OK, stock.ACCEPT, response_cb, 
            cls.entry_cb, *args)

        setattr(window, 'entry', entry)

        entry.show()

        return window

    @classmethod
    def add_button(cls, window, gtk_stock, stock_id, response_cb,
        callback, *args):
        '''add a button and connect the signal'''
        button = gtk.Button(stock=gtk_stock)
        window.bbox.pack_start(button, True, True)
        button.connect('clicked', callback, window, response_cb,
            stock_id, *args)

        button.show()

        return button
        
    @classmethod
    def new_window(cls, title, response_cb=None, *args):
        '''build a window with the default values and connect the common
        signals, return the window'''

        window = gtk.Window()
        window.set_title(title)
        window.set_default_size(150, 100)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_border_width(8)
        window.set_icon(utils.safe_gtk_image_load(gui.theme.logo).get_pixbuf())

        vbox = gtk.VBox(spacing=4)
        hbox = gtk.HBox(spacing=4)
        bbox = gtk.HButtonBox()
        bbox.set_spacing(4)
        bbox.set_layout(gtk.BUTTONBOX_END)

        vbox.pack_start(hbox, True, True)
        vbox.pack_start(bbox, False)

        window.add(vbox)

        setattr(window, 'vbox', vbox)
        setattr(window, 'hbox', hbox)
        setattr(window, 'bbox', bbox)

        args = list(args)
        args.insert(0, stock.CLOSE)
        window.connect('delete-event', cls.close_cb, window,
            response_cb, *args)

        vbox.show_all()

        return window

    @classmethod
    def error(cls, message, response_cb=None, title=_("Error!")):
        '''show an error dialog displaying the message, this dialog should
        have only the option to close and the response callback is optional
        since in few cases one want to know when the error dialog was closed,
        but it can happen, so return stock.CLOSE to the callback if its set'''
        cls.message_window(message, gtk.STOCK_DIALOG_ERROR, response_cb, 
            title).show()

    @classmethod
    def warning(cls, message, response_cb=None, title=_("Warning")):
        '''show a warning dialog displaying the messge, this dialog should
        have only the option to accept, like the error dialog, the response
        callback is optional, but you have to check if it's not None and
        send the response (that can be stock.ACCEPT or stock.CLOSE, if
        the user closed the window with the x)'''
        cls.message_window(message, gtk.STOCK_DIALOG_WARNING, response_cb, 
            title).show()

    @classmethod
    def information(cls, message, response_cb=None, 
                            title=_("Information"),):
        '''show a warning dialog displaying the messge, this dialog should
        have only the option to accept, like the error dialog, the response
        callback is optional, but you have to check if it's not None and
        send the response (that can be stock.ACCEPT or stock.CLOSE, if
        the user closed the window with the x)'''
        cls.message_window(message, gtk.STOCK_DIALOG_INFO, response_cb, 
            title).show()

    @classmethod
    def exception(cls, message, response_cb=None, title=_("Exception"),):
        '''show the message of an exception on a dialog, useful to
        connect with sys.excepthook'''
        window = cls.new_window(title, response_cb)
        label = cls.window_add_label(window, message)
        cls.add_button(window, gtk.STOCK_CLOSE, stock.CLOSE, response_cb,
            cls.default_cb)
        cls.window_add_label(window, label)

        window.show()

    @classmethod
    def yes_no(cls, message, response_cb, *args):
        '''show a confirm dialog displaying a question and two buttons:
        Yes and No, return the response as stock.YES or stock.NO or
        stock.CLOSE if the user closes the window'''
        window = cls.common_window(message, gtk.STOCK_DIALOG_QUESTION, 
            response_cb, _("Confirm"))
        cls.add_button(window, gtk.STOCK_YES, stock.YES, response_cb, 
            cls.default_cb, *args)
        cls.add_button(window, gtk.STOCK_NO, stock.NO, response_cb, 
            cls.default_cb, *args)

        window.show()

    @classmethod
    def yes_no_cancel(cls, message, response_cb, *args):
        '''show a confirm dialog displaying a question and three buttons:
        Yes and No and Cancel, return the response as stock.YES, stock.NO,
        stock.CANCEL or stock.CLOSE if the user closes the window'''
        window = cls.common_window(message, gtk.STOCK_DIALOG_QUESTION, 
            response_cb, _("Confirm"))
        cls.add_button(window, gtk.STOCK_YES, stock.YES, response_cb, 
            cls.default_cb, *args)
        cls.add_button(window, gtk.STOCK_NO, stock.NO, response_cb, 
            cls.default_cb, *args)
        cls.add_button(window, gtk.STOCK_CANCEL, stock.CANCEL, response_cb, 
            cls.default_cb, *args)

        window.show()

    @classmethod
    def accept_cancel(cls, message, response_cb, *args):
        '''show a confirm dialog displaying information and two buttons:
        Accept and Cancel, return stock.ACCEPT, stock.CANCEL or 
        stock.CLOSE'''
        window = cls.common_window(message, gtk.STOCK_DIALOG_QUESTION, 
            response_cb, _("Confirm"))
        cls.add_button(window, gtk.STOCK_OK, stock.ACCEPT, response_cb, 
            cls.default_cb, *args)
        cls.add_button(window, gtk.STOCK_CANCEL, stock.CANCEL, response_cb, 
            cls.default_cb, *args)

        window.show()

    @classmethod
    def contact_added_you(cls, accounts, response_cb, 
                                title=_("User invitation")):
        '''show a dialog displaying information about users
        that added you to their userlists, the accounts parameter is
        a tuple of mails that represent all the users that added you,
        the way you confirm (one or more dialogs) doesn't matter, but
        you should call the response callback only once with a tuple
        like: ((mail1, stock.YES), (mail2, stock.NO), (mail3, stock.CANCEL))
        YES means add him to your userlist, NO means block him, CANCEL
        means remind me later.'''
        raise NotImplementedError("This method isn't implemented")

    @classmethod
    def add_contact(cls, groups, group_selected, response_cb, 
        title=_("Add user")):
        '''show a dialog asking for an user address, and (optional)
        the group(s) where the user should be added, the response callback
        receives the response type (stock.ADD, stock.CANCEL or stock.CLOSE)
        the account and a tuple of group names where the user should be 
        added (give a empty tuple if you don't implement this feature, 
        the controls are made by the callback, you just ask for the email, 
        don't make any control, you are just implementing a GUI! :P'''
        window = cls.new_window(title, response_cb)
        label = gtk.Label(_("Account"))
        label_align = gtk.Alignment(0.0, 0.5)
        label_align.add(label)
        entry = gtk.Entry()
        group_label = gtk.Label(_("Group"))
        group_label_align = gtk.Alignment(0.0, 0.5)
        group_label_align.add(group_label)
        combo = gtk.combo_box_new_text()

        combo.append_text("")

        groups = list(groups)
        groups.sort()

        selected = 0

        for (index, group) in enumerate(groups):
            combo.append_text(group.name)

            if group_selected == group.name:
                selected = index + 1

        combo.set_active(selected)

        table = gtk.Table(2, 2)
        table.attach(label_align, 0, 1, 0, 1)
        table.attach(entry, 1, 2, 0, 1)
        table.attach(group_label_align, 0, 1, 1, 2)
        table.attach(combo, 1, 2, 1, 2)
        table.set_row_spacings(2)
        table.set_col_spacings(8)

        window.hbox.pack_start(table, True, True)

        cls.add_button(window, gtk.STOCK_CANCEL, stock.CANCEL, response_cb, 
            cls.add_contact_cb)
        cls.add_button(window, gtk.STOCK_OK, stock.ACCEPT, response_cb, 
            cls.add_contact_cb)

        setattr(window, 'entry', entry)
        setattr(window, 'combo', combo)

        entry.connect('activate', cls.add_contact_cb, window, response_cb,
            stock.ACCEPT)
        window.show_all()

    @classmethod
    def add_group(cls, response_cb, title=_("Add group")):
        '''show a dialog asking for a group name, the response callback
        receives the response (stock.ADD, stock.CANCEL, stock.CLOSE)
        and the name of the group, the control for a valid group is made
        on the controller, so if the group is empty you just call the
        callback, to make a unified behaviour, and also, to only implement
        GUI logic on your code and not client logic
        cb args: response, group_name'''
        window = cls.entry_window(_("Group name"), '', response_cb, title)
        window.show()

    @classmethod
    def set_nick(cls, nick, response_cb, title=_("Change nick")):
        '''show a dialog asking for a new nick and displaying the current
        one, the response_cb receives the old nick, the new nick, 
        and the response (stock.ACCEPT, stock.CANCEL or stock.CLOSE)
        cb args: response, old_nick, new_nick'''
        window = cls.entry_window(_("New nick"), nick, response_cb, title,
        nick)
        window.show()

    @classmethod
    def set_message(cls, message, response_cb, 
        title=_("Change personal message")):
        '''show a dialog asking for a new personal message and displaying 
        the current one, the response_cb receives the old personal message
        , the new personal message and the response 
        (stock.ACCEPT, stock.CANCEL or stock.CLOSE)
        cb args: response, old_pm, new_pm'''
        window = cls.entry_window(_("New personal message"), 
            message, response_cb, title, message)
        window.show()

    @classmethod
    def rename_group(cls, group, response_cb, title=_("Rename group")):
        '''show a dialog with the group name and ask to rename it, the
        response callback receives stock.ACCEPT, stock.CANCEL or stock.CLOSE
        the old and the new name.
        cb args: response, old_name, new_name
        '''
        window = cls.entry_window(_("New group name"), group.name, response_cb, 
            title, group)
        window.show()

    @classmethod
    def set_contact_alias(cls, account, alias, response_cb, 
                            title=_("Set alias")):
        '''show a dialog showing the current alias and asking for the new
        one, the response callback receives,  the response 
        (stock.ACCEPT, stock.CANCEL, stock.CLEAR <- to remove the alias 
        or stock.CLOSE), the account, the old and the new alias.
        cb args: response, account, old_alias, new_alias'''
        alias = alias or ''
        window = cls.entry_window(_("Contact alias"), alias, response_cb, 
            title, account, alias)
        cls.add_button(window, gtk.STOCK_CLEAR, stock.CLEAR, response_cb,
            cls.entry_cb, account, alias)
        window.show()

    @classmethod
    def about_dialog(cls, name, version, copyright, comments, license, website,
        authors, translators, logo_path):
        '''show an about dialog of the application:
        * title: the title of the window
        * name: the name of the appliaction
        * version: version as string
        * copyright: the name of the copyright holder
        * comments: a description of the application
        * license: the license text
        * website: the website url
        * authors: a list or tuple of strings containing the contributors
        * translators: a string containing the translators
        '''

        about = gtk.AboutDialog()
        about.set_name(name)
        about.set_version(version)
        about.set_copyright(copyright)
        about.set_comments(comments)
        about.set_license(license)
        about.set_website(website)

        about.set_authors(authors)
        about.set_translator_credits(translators)
        icon = gtk.gdk.pixbuf_new_from_file(logo_path)
        about.set_icon(icon)
        about.set_logo(icon)
        about.run()
        about.hide()

    @classmethod
    def contact_information_dialog(cls, session, account):
        '''shows information about the account'''
        ContactInformation.ContactInformation(session, account).show()

    @classmethod
    def select_font(cls, style, callback):
        '''select font and if available size and style, receives a 
        protocol.Message.Style object with the current style
        the callback receives a new style object with the new selection
        '''
        def select_font_cb(button, window, callback, response, color_sel, 
            color):
            '''callback called on button selection'''
            if response == stock.ACCEPT:
                window.hide()
                fdesc = pango.FontDescription(font_sel.get_font_name())
                style = utils.pango_font_description_to_style(fdesc)
                style.color.red = color.red
                style.color.green = color.green
                style.color.blue = color.blue
                style.color.alpha = color.alpha

                callback(style)

            window.hide()

        window = cls.new_window('Select font')

        font_sel = gtk.FontSelection()
        font_sel.set_preview_text('OMG PONNIES! I\'m a preview text!')
        fdesc = utils.style_to_pango_font_description(style)

        window.hbox.pack_start(font_sel, True, True)
        font_sel.set_font_name(fdesc.to_string())

        cls.add_button(window, gtk.STOCK_CANCEL, stock.CANCEL, callback, 
            select_font_cb, font_sel, style.color)
        cls.add_button(window, gtk.STOCK_OK, stock.ACCEPT, callback, 
            select_font_cb, font_sel, style.color)
        window.show_all()

    @classmethod
    def select_color(cls, color, callback):
        '''select color, receives a protocol.Message.Color with the current 
        color the callback receives a new color object woth the new selection
        '''

        def select_color_cb(button, window, callback, response, color_sel):
            '''callback called on button selection'''

            if response == stock.ACCEPT:
                window.hide()
                gtk_color = color_sel.get_current_color()
                color = protocol.Color(gtk_color.red, gtk_color.green, 
                    gtk_color.blue)
                callback(color)

            window.hide()

        window = cls.new_window('Select color')

        color_sel = gtk.ColorSelection()

        window.hbox.pack_start(color_sel, True, True)
        color_sel.set_current_color(gtk.gdk.color_parse('#' + color.to_hex()))

        cls.add_button(window, gtk.STOCK_CANCEL, stock.CANCEL, callback, 
            select_color_cb, color_sel)
        cls.add_button(window, gtk.STOCK_OK, stock.ACCEPT, callback, 
            select_color_cb, color_sel)
        window.show_all()

    @classmethod
    def select_style(cls, style, callback):
        '''select bold, italic, underline and strike, receives 
        a protocol.Message.Style object with the current style
        the callback receives the response and a new style object with the 
        selection
        '''
        pass

    @classmethod
    def select_emote(cls, theme, callback, max_width=8):
        '''select an emoticon, receives a gui.Theme object with the theme 
        settings the callback receives the response and a string representing 
        the selected emoticon
        '''
        EmotesWindow(callback, max_width).show()

    @classmethod
    def invite_dialog(cls, session, callback):
        '''select a contact to add to the conversation, receives a session 
        object of the current session the callback receives the response and 
        a string containing the selected account
        '''
        pass

    @classmethod
    def login_preferences(cls, session, callback, use_http, proxy):
        """
        display the preferences dialog for the login window

        cls -- the dialog class
        session -- the session string identifier
        callback -- callback to call if the user press accept, call with the
            new values
        use_http -- boolean that indicates if the protocol should use http
            method
        proxy -- a protocol.Proxy object
        """

        content = gtk.VBox()
        box = gtk.Table(9, 2)

        combo = gtk.combo_box_new_text()

        t_host = gtk.Entry()
        t_port = gtk.Entry()
        t_user = gtk.Entry()
        t_passwd = gtk.Entry()

        def on_toggled(check_button, *entries):
            '''called when a check button is toggled, receive a set
            of entries, enable or disable them deppending on the state
            of the check button'''
            for entry in entries:
                entry.set_sensitive(check_button.get_active())

        c_use_http = gtk.CheckButton('Use HTTP method')
        c_use_proxy = gtk.CheckButton('Use proxy')
        c_use_proxy.connect('toggled', on_toggled, t_host, t_port)
        c_use_auth = gtk.CheckButton('Use authentication')
        c_use_auth.connect('toggled', on_toggled, t_user, t_passwd)

        t_host.set_text(proxy.host or '')
        t_port.set_text(proxy.port or '')
        t_user.set_text(proxy.user or '')
        t_passwd.set_text(proxy.passwd or '')
        t_passwd.set_visibility(False)
        c_use_http.set_active(use_http)
        c_use_proxy.set_active(proxy.use_proxy)
        c_use_proxy.toggled()
        c_use_proxy.toggled()
        c_use_auth.set_active(proxy.use_auth)
        c_use_auth.toggled()
        c_use_auth.toggled()

        l_session = gtk.Label('Session')
        l_session.set_alignment(0.0, 0.5)
        l_host = gtk.Label('Host')
        l_host.set_alignment(0.0, 0.5)
        l_port = gtk.Label('Port')
        l_port.set_alignment(0.0, 0.5)
        l_user = gtk.Label('User')
        l_user.set_alignment(0.0, 0.5)
        l_passwd = gtk.Label('Password')
        l_passwd.set_alignment(0.0, 0.5)

        box.attach(l_session, 0, 1, 0, 1)
        box.attach(combo, 1, 2, 0, 1)
        box.attach(c_use_http, 0, 2, 1, 2)
        box.attach(c_use_proxy, 0, 2, 2, 3)
        box.attach(l_host, 0, 1, 3, 4)
        box.attach(t_host, 1, 2, 3, 4)
        box.attach(l_port, 0, 1, 4, 5)
        box.attach(t_port, 1, 2, 4, 5)
        box.attach(c_use_auth, 0, 2, 5, 6)
        box.attach(l_user, 0, 1, 6, 7)
        box.attach(t_user, 1, 2, 6, 7)
        box.attach(l_passwd, 0, 1, 7, 8)
        box.attach(t_passwd, 1, 2, 7, 8)

        index = 0
        count = 0
        name_to_id = {}
        for ext_id, ext in extension.get_extensions('session').iteritems():
            if session == ext_id:
                index = count

            combo.append_text(ext.NAME)
            name_to_id[ext.NAME] = ext_id
            count += 1

        combo.set_active(index)

        def response_cb(response):
            '''called on any response (close, accept, cancel) if accept
            get the new values and call callback with those values'''
            if response == stock.ACCEPT:
                use_http = c_use_http.get_active()
                use_proxy = c_use_proxy.get_active()
                use_auth = c_use_auth.get_active()
                host = t_host.get_text()
                port = t_port.get_text()
                user = t_user.get_text()
                passwd = t_passwd.get_text()

                session_id = name_to_id[combo.get_active_text()]
                callback(use_http, use_proxy, host, port, use_auth, user, passwd, 
                    session_id)

            window.hide()

        def button_cb(button, window, response_cb, response):
            '''called when a button is pressedm get the response id and call
            the response_cb that will handle the event according to the 
            response'''
            response_cb(response)

        window = cls.new_window('Preferences', response_cb)
        window.hbox.pack_start(content, True, True)
        content.pack_start(box, True, True)

        cls.add_button(window, gtk.STOCK_CANCEL, stock.CANCEL, response_cb, button_cb)
        cls.add_button(window, gtk.STOCK_OK, stock.ACCEPT, response_cb, button_cb)
        window.show_all()

class EmotesWindow(gtk.Window):
    """
    This class represents a window to select an emoticon
    """

    def __init__(self, emote_selected, max_width=8):
        """
        Constructor.
        max_width -- the maximum number of columns
        """
        gtk.Window.__init__(self)
        self.set_decorated(False)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_position(gtk.WIN_POS_MOUSE)
        self.set_resizable(False)

        self.max_width = max_width
        self.emote_selected = emote_selected

        emotes_count = gui.theme.get_emotes_count()
        rows = emotes_count/max_width
        self.table = gtk.Table(max_width, rows)

        self._fill_emote_table(max_width)

        box = gtk.VBox()
        box.pack_start(self.table)
        self.add(box)
        box.show_all()

    def _fill_emote_table(self, columns):
        '''fill the gtk.Table with the emoticons'''
        emotes = []

        count = 0
        for shortcut, name in gui.theme.EMOTES.iteritems():
            if name in emotes:
                continue

            column = count % columns
            row = count / columns
            button = gtk.Button()
            path = gui.theme.emote_to_path(shortcut, True)

            if path is None:
                dbg(shortcut + ' has no path', 'dialog', 1)
                continue

            button.set_image(utils.safe_gtk_image_load(path))
            button.connect('clicked', self._on_emote_selected, shortcut)
            self.table.attach(button, column, column + 1, row, row + 1)

            count += 1

    def _on_emote_selected(self, button, shortcut):
        '''called when an emote is selected'''
        self.emote_selected(shortcut)
        self.hide()

