#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016, Cristian García <cristian99garcia@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from gettext import gettext as _

from utils import make_separator
from utils import get_icon_name
from utils import get_body_name
from constants import Screen
from constants import BodyName
from constants import CelestialBodyType
from constants import Speed

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.radiotoolbutton import RadioToolButton
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton
from sugar3.graphics.toolbarbox import ToolbarBox as SugarToolbarBox
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton


class ToolbarInfo(Gtk.Toolbar):

    __gsignals__ = {
        "show-simulation": (GObject.SIGNAL_RUN_FIRST, None, []),
        "show-info": (GObject.SIGNAL_RUN_FIRST, None, []),
        "go-back": (GObject.SIGNAL_RUN_FIRST, None, []),
        "go-forward": (GObject.SIGNAL_RUN_FIRST, None, []),
    }

    def __init__(self):
        Gtk.Toolbar.__init__(self)

        self.button = ToolbarButton(page=self, icon_name="info")

        self.button_simulation = RadioToolButton(icon_name="solar-system", group=None)
        self.button_simulation.set_tooltip(_("Show solar system"))
        self.button_simulation.connect("toggled", self._show_simulation_cb)
        self.insert(self.button_simulation, -1)

        self.button_info = RadioToolButton(icon_name="info", group=self.button_simulation)
        self.button_info.set_tooltip(_("Show information"))
        self.button_info.connect("toggled", self._show_info_cb)
        self.insert(self.button_info, -1)

        self.insert(make_separator(False), -1)

        self.back_button = ToolButton("go-previous-paired")
        self.back_button.set_tooltip(_("Go back"))
        self.back_button.set_sensitive(False)
        self.back_button.connect("clicked", self._go_back_cb)
        self.insert(self.back_button, -1)

        self.forward_button = ToolButton("go-next-paired")
        self.forward_button.set_tooltip(_("Go forward"))
        self.forward_button.set_sensitive(False)
        self.forward_button.connect("clicked", self._go_forward_cb)
        self.insert(self.forward_button, -1)

        self.show_all()

    def _show_simulation_cb(self, widget):
        self.emit("show-simulation")

    def _show_info_cb(self, widget):
        self.emit("show-info")

    def _go_back_cb(self, widget):
        self.emit("go-back")

    def _go_forward_cb(self, widget):
        self.emit("go-forward")

    def select_screen(self, screen):
        if screen == Screen.SOLAR_SYSTEM:
            self.button_simulation.props = True

        elif screen == Screen.INFO:
            self.button_info.props.active = True


class ToolbarView(Gtk.Toolbar):

    __gsignals__ = {
        "show-orbits": (GObject.SIGNAL_RUN_FIRST, None, [bool]),
        "show-body": (GObject.SIGNAL_RUN_FIRST, None, [int, bool]),
        "zoom-changed": (GObject.SIGNAL_RUN_FIRST, None, [float]),
    }

    def __init__(self):
        Gtk.Toolbar.__init__(self)

        self.button = ToolbarButton(page=self, icon_name="toolbar-view")

        self.buttons = {
            CelestialBodyType.MERCURY: None,
            CelestialBodyType.VENUS: None,
            CelestialBodyType.EARTH: None,
            CelestialBodyType.MARS: None,
            CelestialBodyType.JUPITER: None,
            CelestialBodyType.SATURN: None,
            CelestialBodyType.URANUS: None,
            CelestialBodyType.NEPTUNE: None
        }

        self.orbits_button = ToggleToolButton("show-orbits")
        self.orbits_button.set_tooltip(_("Show planets orbits"))
        self.orbits_button.connect("toggled", self._show_orbits_cb)
        self.insert(self.orbits_button, -1)

        self.insert(make_separator(False), -1)

        for planet in self.buttons:
            button = ToggleToolButton(get_icon_name(planet))
            button.set_tooltip(get_body_name(planet))
            button.set_active(True)
            button.connect("toggled", self._show_planet_cb, planet)
            self.insert(button, -1)

            self.buttons[planet] = button

        self.insert(make_separator(False), -1)

        adj = Gtk.Adjustment(1, 0.8, 500, 0.5, 1)
        self.zoom_scale = Gtk.HScale()
        self.zoom_scale.set_draw_value(False)
        self.zoom_scale.set_adjustment(adj)
        self.zoom_scale.set_size_request(200, 1)
        self.zoom_scale.connect("value-changed", self._zoom_changed_cb)

        self.zoom_out = ToolButton("zoom-out")
        self.zoom_out.set_tooltip(_("Zoom out"))
        self.zoom_out.connect("clicked", self._zoom_out_cb)
        self.insert(self.zoom_out, -1)

        item = Gtk.ToolItem()
        item.add(self.zoom_scale)
        self.insert(item, -1)

        self.zoom_in = ToolButton("zoom-in")
        self.zoom_in.set_tooltip(_("Zoom in"))
        self.zoom_in.connect("clicked", self._zoom_in_cb)
        self.insert(self.zoom_in, -1)

        self.show_all()

    def disable_simulation_widgets(self):
        self.orbits_button.set_sensitive(False)
        for planet in self.buttons:
            self.buttons[planet].set_sensitive(False)

        self.zoom_scale.set_sensitive(False)
        self.zoom_out.set_sensitive(False)
        self.zoom_in.set_sensitive(False)

    def enable_simulation_widgets(self):
        self.orbits_button.set_sensitive(True)
        for planet in self.buttons:
            self.buttons[planet].set_sensitive(True)

        self.zoom_scale.set_sensitive(True)
        self.zoom_out.set_sensitive(True)
        self.zoom_in.set_sensitive(True)

    def _show_orbits_cb(self, button):
        self.emit("show-orbits", button.get_active())

    def _show_planet_cb(self, button, planet):
        self.emit("show-body", planet, button.get_active())

    def _zoom_changed_cb(self, scale):
        self.emit("zoom-changed", scale.get_value())

    def _zoom_out_cb(self, widget):
        new_value = self.zoom_scale.get_value() - 2.5
        lower_value = self.zoom_scale.get_adjustment().get_lower()
        if new_value < lower_value:
            self.zoom_scale.set_value(lower_value)

        else:
            self.zoom_scale.set_value(new_value)

    def _zoom_in_cb(self, widget):
        new_value = self.zoom_scale.get_value() + 2.5
        upper = self.zoom_scale.get_adjustment().get_upper()
        if new_value > upper:
            self.zoom_scale.set_value(upper)

        else:
            self.zoom_scale.set_value(new_value)


class ToolbarSpeed(Gtk.Toolbar):

    __gsignals__ = {
        "speed-changed": (GObject.SIGNAL_RUN_FIRST, None, [float]),
    }

    def __init__(self):
        Gtk.Toolbar.__init__(self)

        self.button = ToolbarButton(page=self, icon_name="media-playback-stop")
        self.playing = True
        self.speed = None

        self.stop_play = ToolButton("media-playback-stop")
        self.stop_play.set_tooltip(_("Stop"))
        self.stop_play.connect("clicked", self._stop_play)
        self.insert(self.stop_play, -1)

        self.slow_button = RadioToolButton(group=None, icon_name="slow-walk-milton-raposo")
        self.slow_button.set_tooltip(_("Run slow"))
        self.slow_button.connect("clicked", self._speed_changed_cb, Speed.SLOW)
        self.insert(self.slow_button, -1)

        self.normal_button = RadioToolButton(group=self.slow_button, icon_name="walking")
        self.normal_button.set_tooltip(_("Run Normal"))
        self.normal_button.connect("clicked", self._speed_changed_cb, Speed.NORMAL)
        self.insert(self.normal_button, -1)

        self.fast_button = RadioToolButton(group=self.slow_button, icon_name="running")
        self.fast_button.set_tooltip(_("Run fast"))
        self.fast_button.connect("clicked", self._speed_changed_cb, Speed.FAST)
        self.insert(self.fast_button, -1)

        self.normal_button.set_active(True)

        self.show_all()

    def _stop_play(self, button=None):
        self.playing = not self.playing

        if self.playing:
            self.stop_play.set_icon_name("media-playback-stop")
            self.stop_play.set_tooltip(_("Stop"))
            self.button.set_icon_name("media-playback-stop")

            self.emit("speed-changed", self.speed)

        else:
            self.stop_play.set_icon_name("media-playback-start")
            self.stop_play.set_tooltip(_("Start"))
            self.button.set_icon_name("media-playback-start")

            self.emit("speed-changed", Speed.STOPPED)

    def _speed_changed_cb(self, button, speed):
        if not self.playing:
            self.speed = speed
            self._stop_play()

        else:
            self.emit("speed-changed", speed)
            self.speed = speed

    def enable(self):
        self.set_sensitive_buttons(True)

    def disable(self):
        self.set_sensitive_buttons(False)

    def set_sensitive_buttons(self, sensitive):
        self.stop_play.set_sensitive(sensitive)
        self.slow_button.set_sensitive(sensitive)
        self.normal_button.set_sensitive(sensitive)
        self.fast_button.set_sensitive(sensitive)


class ToolbarBox(SugarToolbarBox):

    __gsignals__ = {
        "show-simulation": (GObject.SIGNAL_RUN_FIRST, None, []),
        "show-info": (GObject.SIGNAL_RUN_FIRST, None, []),
        "go-back": (GObject.SIGNAL_RUN_FIRST, None, []),
        "go-forward": (GObject.SIGNAL_RUN_FIRST, None, []),
        "show-orbits": (GObject.SIGNAL_RUN_FIRST, None, [bool]),
        "show-body": (GObject.SIGNAL_RUN_FIRST, None, [int, bool]),
        "speed-changed": (GObject.SIGNAL_RUN_FIRST, None, [float]),
        "zoom-changed": (GObject.SIGNAL_RUN_FIRST, None, [float]),
    }

    def __init__(self, activity):
        SugarToolbarBox.__init__(self)

        activity_button = ActivityToolbarButton(activity)
        self.toolbar.insert(activity_button, -1)

        self.toolbar.insert(make_separator(False), -1)

        self.toolbar_info = ToolbarInfo()
        self.toolbar_info.connect("show-simulation", self._show_simulation_cb)
        self.toolbar_info.connect("show-info", self._show_info_cb)
        self.toolbar_info.connect("go-back", self._go_back_cb)
        self.toolbar_info.connect("go-forward", self._go_forward_cb)
        self.toolbar.insert(self.toolbar_info.button, -1)

        self.toolbar_view = ToolbarView()
        self.toolbar_view.connect("show-orbits", self._show_orbits_cb)
        self.toolbar_view.connect("show-body", self._show_body_cb)
        self.toolbar_view.connect("zoom-changed", self._zoom_changed_cb)
        self.toolbar.insert(self.toolbar_view.button, -1)

        self.toolbar_speed = ToolbarSpeed()
        self.toolbar_speed.connect("speed-changed", self._speed_changed_cb)
        self.toolbar.insert(self.toolbar_speed.button, -1)

        self.toolbar.insert(make_separator(True), -1)

        stop_button = StopButton(activity)
        self.toolbar.insert(stop_button, -1)

    def set_can_back_back(self, can):
        self.toolbar_info.button_back.set_sensitive(can)

    def set_can_go_forward(self, can):
        self.toolbar_info.forward_button.set_sensitive(can)

    def disable_simulation_widgets(self):
        self.toolbar_view.disable_simulation_widgets()
        self.toolbar_speed.disable()

    def enable_simulation_widgets(self):
        self.toolbar_view.enable_simulation_widgets()
        self.toolbar_speed.enable()

    def _show_simulation_cb(self, widget):
        self.emit("show-simulation")

    def _show_info_cb(self, widget):
        self.emit("show-info")

    def _go_back_cb(self, widget):
        self.emit("go-back")

    def _go_forward_cb(self, widget):
        self.emit("go-forward")

    def _speed_changed_cb(self, toolbar, speed):
        self.emit("speed-changed", speed)

    def _show_orbits_cb(self, toolbar, show):
        self.emit("show-orbits", show)

    def _show_body_cb(self, toolbar, body, show):
        self.emit("show-body", body, show)

    def _zoom_changed_cb(self, toolbar, zoom):
        self.emit("zoom-changed", zoom)

    def select_screen(self, screen):
        self.toolbar_info.select_screen(screen)

    def set_can_go_forward(self, can):
        self.toolbar_info.forward_button.set_sensitive(can)

    def set_can_go_back(self, can):
        self.toolbar_info.back_button.set_sensitive(can)
