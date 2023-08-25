import os

import gi
from abc import ABCMeta, abstractmethod

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ..constants import (ICON_DIR_PATH, VPN_TRAY_ERROR, VPN_TRAY_OFF,
                         VPN_TRAY_ON)
from ..enums import IndicatorActionEnum
from ..logger import logger
from ..rx.subject.replaysubject import ReplaySubject


def generate_protonvpn_indicator(gtk_application):
    try:
        return ProtonVPNIndicator(gtk_application)
    except ValueError:
        return DummyIndicator()


class MetaIndicator(metaclass=ABCMeta):

    @property
    @abstractmethod
    def application():
        pass

    @property
    @abstractmethod
    def indicator(self):
        pass

    @property
    @abstractmethod
    def login_action(self):
        pass

    @property
    @abstractmethod
    def dashboard_action(self):
        pass

    @abstractmethod
    def set_connected_state():
        pass

    @abstractmethod
    def set_disconnected_state():
        pass

    @abstractmethod
    def set_error_state():
        pass

    @abstractmethod
    def setup_reply_subject():
        pass


class DummyIndicator(MetaIndicator):
    """Dummy class"""
    _type = "dummy"

    @property
    def application():
        return None

    @property
    def indicator(self):
        return None

    @property
    def login_action(self):
        return None

    @property
    def dashboard_action(self):
        return None

    def set_connected_state(self, *args, **kwargs):
        """Dummy method"""
        pass

    def set_disconnected_state(self, *args, **kwargs):
        """Dummy method"""
        pass

    def set_error_state(self, *args, **kwargs):
        """Dummy method"""
        pass

    def setup_reply_subject(self):
        """Dummy method"""
        pass


class ProtonVPNIndicator(MetaIndicator):
    _type = "indicator"

    def __init__(self, application):
        gi.require_version("AppIndicator3", "0.1")
        from gi.repository import AppIndicator3 as appindicator
        self.setup_reply_subject()
        self.__application = application
        self.__generate_menu()
        self.__indicator = appindicator.Indicator.new(
            "Proton VPN Tray",
            "protonvpn-tray",
            appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.__indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.__indicator.set_menu(self.__menu)
        self.__indicator.set_icon_theme_path(ICON_DIR_PATH)
        self.__indicator.set_icon_full(VPN_TRAY_OFF, "protonvpn")

    @property
    def application(self):
        return self.__application

    @property
    def indicator(self):
        return self.__indicator

    @property
    def login_action(self):
        return self.__indicator_login_action

    @property
    def dashboard_action(self):
        return self.__indicator_dashboard_action

    def __generate_menu(self):
        self.__menu = Gtk.Menu()

        self.__separator_0 = Gtk.SeparatorMenuItem()
        self.__menu.append(self.__separator_0)
        self.__separator_0.show()

        self.__quick_connect_item = Gtk.MenuItem(label="Quick Connect")
        self.__quick_connect_item.connect("activate", self.__quick_connect)
        self.__menu.append(self.__quick_connect_item)
        self.__quick_connect_item.hide()

        self.__disconnect_item = Gtk.MenuItem(label="Disconnect")
        self.__disconnect_item.connect("activate", self.__disconnect)
        self.__menu.append(self.__disconnect_item)
        self.__disconnect_item.hide()

        self.__separator_1 = Gtk.SeparatorMenuItem()
        self.__menu.append(self.__separator_1)
        self.__separator_1.show()

        self.__show_gui_item = Gtk.MenuItem(label="Show Proton VPN")
        self.__show_gui_item.connect("activate", self.__show_gui)
        self.__menu.append(self.__show_gui_item)
        self.__show_gui_item.show()

        self.__separator_2 = Gtk.SeparatorMenuItem()
        self.__menu.append(self.__separator_2)
        self.__separator_2.show()

        self.__exit_tray_item = Gtk.MenuItem(label="Quit")
        self.__exit_tray_item.connect("activate", self.__quit_protonvpn)
        self.__menu.append(self.__exit_tray_item)
        self.__exit_tray_item.show()

        return self.__menu

    def __quick_connect(self, _):
        """Makes a quick connection by making a cli call to protonvpn-cli-ng"""
        self.on_next_reply(IndicatorActionEnum.QUICK_CONNECT)

    def __disconnect(self, _):
        """__disconnects from a current vpn connection"""
        self.on_next_reply(IndicatorActionEnum.DISCONNECT)

    def __show_gui(self, _):
        """Displays the GUI."""
        self.on_next_reply(IndicatorActionEnum.SHOW_GUI)

    def __quit_protonvpn(self, _):
        """Quit/Stop the tray icon.
        """
        self.__application.on_quit()

    def on_next_reply(self, indicator_enum):
        from protonvpn_gui.rx.internal.exceptions import DisposedException
        try:
            self.__indicator_dashboard_action.on_next(indicator_enum)
        except DisposedException:
            pass
        except Exception as e:
            logger.exception(e)

        try:
            self.__indicator_login_action.on_next(indicator_enum)
        except DisposedException:
            pass
        except Exception as e:
            logger.exception(e)

    def set_connected_state(self):
        self.__indicator.set_icon_full(VPN_TRAY_ON, "protonvpn")
        self.__quick_connect_item.hide()
        self.__disconnect_item.show()

    def set_disconnected_state(self, hide_quick_connect=False):
        self.__indicator.set_icon_full(VPN_TRAY_OFF, "protonvpn")
        self.__disconnect_item.hide()
        if hide_quick_connect:
            self.__quick_connect_item.hide()
            return

        self.__quick_connect_item.show()

    def set_error_state(self):
        self.__indicator.set_icon_full(VPN_TRAY_ERROR, "protonvpn")

    def setup_reply_subject(self):
        self.__indicator_login_action = ReplaySubject(buffer_size=1)
        self.__indicator_dashboard_action = ReplaySubject(buffer_size=1)
