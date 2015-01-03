#!/usr/bin/env python

# Copyright (C) 2015 by Mike Sajak
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import gtk
import appindicator
import gobject
import pytz
import datetime
import subprocess
import re

class AppIndicator (appindicator.Indicator):
    iface_menu_items = []

    iwconfig_cmd = '/sbin/iwconfig'
    ifaces = []
    cur_if = None
    update_time = 5

    def __init__(self, name, icon, category):
        appindicator.Indicator.__init__(self, name, icon, category)
        self.set_status(appindicator.STATUS_ACTIVE)
        self.update()
        self.menu = self.create_menu()
        self.set_menu(self.menu)
        self.menu.show_all()

        gtk.main()

    def set_cur_iff(self, item, iff):
        self.cur_iff = iff

    def set_update_time(self, item, time):
        self.update_time = time

    def create_menu(self):
        menu = gtk.Menu()
        if len(self.ifaces) > 0:
            for iff in self.ifaces:
                item = gtk.MenuItem(iff)
                item.connect('activate', self.set_cur_iff, iff)
                menu.append(item)
        else:
            item = gtk.MenuItem('No wireless interfaces detected')
            item.set_sensitive(False) # disabled - grayed out
            menu.append(item)

        menu.append(gtk.SeparatorMenuItem())
        item = gtk.MenuItem('Update time')
        submenu = gtk.Menu()
        for i in [1,2,3,5,7,10,15,30,45,60]:
            item2 = gtk.MenuItem(str(i) + ' s')
            item2.connect('activate', self.set_update_time, i)
            submenu.append(item2)
        item.set_submenu(submenu)
        menu.append(item)
        menu.append(gtk.SeparatorMenuItem())
        item = gtk.MenuItem('Quit')
        item.connect('activate', self.quit)
        menu.append(item)

        return menu

    def update(self):
        gobject.timeout_add(self.update_time * 1000, self.update)

        self.ifaces = self.get_wifi_interfaces()
        # if interface not selected then select first available
        if self.cur_if is None and len(self.ifaces) > 0:
            self.cur_if = self.ifaces[0]

        # self.update_ifaces_menu_items()

        iff_speed = self.get_wifi_speed(self.cur_if)
        if iff_speed is not None:
            self.set_label(iff_speed, '')
        else:
            self.set_label('X', '')

    def get_wifi_speed(self, iff):
        p = subprocess.Popen([self.iwconfig_cmd, iff], stdout=subprocess.PIPE)
        for line in p.stdout:
            m = re.search('Bit Rate=([\d\.]+) (\S+)', line)
            if m is not None:
                print ("Speed: " + m.group(0))
                return m.group(1) + " " + m.group(2)
        return None

    def get_wifi_interfaces(self):
        p = subprocess.Popen([self.iwconfig_cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        iffs = []
        for line in p.stdout:
            m = re.search('no wireless extensions', line)
            if m is None:
                m = re.search('^(\S+)\s+\S+', line)
                if m is not None:
                    iffs.append(m.group(1))
        print("Iffs: " + str(iffs))
        return iffs

    def quit(self, *data):
        gtk.main_quit()



AppIndicator('world-clock', 'radiotray-off', 0)
