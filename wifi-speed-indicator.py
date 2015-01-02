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


    def __init__(self, name, icon, category):
        appindicator.Indicator.__init__(self, name, icon, category)
        self.set_status(appindicator.STATUS_ACTIVE)
        self.menu = gtk.Menu()
        self.set_menu(self.menu)
        self.update()
        self.menu_setup()
        self.menu.show_all()

        gtk.main()

    def clear_menu_ifaces(self):
        for item in self.iface_menu_items:
            self.menu.remove(item)
        self.iface_menu_items = []

    def update_ifaces_menu_items(self):
        self.clear_menu_ifaces()

        if len(self.ifaces) > 0:
            for iff in self.ifaces:
                label = iff
                item = gtk.MenuItem(label)
                self.iface_menu_items.append(item)
                self.menu.prepend(item)
        else:
            item = gtk.MenuItem('No wireless interfaces detected')
            self.menu.prepend(item)


    def menu_setup(self):
        self.update_ifaces_menu_items()

        self.menu.append(gtk.SeparatorMenuItem())
        # self.menu.append(gtk.MenuItem())
        self.quit_item = gtk.MenuItem("Quit")
        self.menu.append(self.quit_item)
        self.quit_item.connect("activate", self.quit)

    def update(self):
        gobject.timeout_add(5000, self.update)

        self.ifaces = self.get_wifi_interfaces()
        # if interface not selected then select first available
        if self.cur_if is None and len(self.ifaces) > 0:
            self.cur_if = self.ifaces[0]

        self.update_ifaces_menu_items()

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



AppIndicator('world-clock', 'radiotray-on', 0)
