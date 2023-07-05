import os
import sys
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gio, Gtk

if Gtk.MINOR_VERSION < 24:
    from .view.incompatible_version_dialog import display_dialog
    display_dialog()
    sys.exit()

from proton.constants import VERSION as proton_version
from protonvpn_nm_lib import exceptions
from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.constants import APP_VERSION as lib_version

from .enums import GTKPriorityEnum
from .constants import APP_VERSION
from .logger import logger
from .patterns.factory import BackgroundProcess
from .view.dashboard import DashboardView
from .view.dialog import (AboutDialog, DisplayMessageDialog, LogoutDialog,
                          QuitDialog)
from .view.indicator import generate_protonvpn_indicator
from .view.login import LoginView


class ProtonVPNGUI(Gtk.Application):
    """Proton VPN GTK Application.

    Windows are composite objects. Follows
    MVVM pattern.
    """

    def __init__(self):
        super().__init__(
            application_id='com.protonvpn.www',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.indicator = None
        self.is_logging_out = False
        self.__main_context = None
        self.__is_app_being_held = False
        self.register()

    @property
    def hold_app(self):
        return self.__is_app_being_held

    @hold_app.setter
    def hold_app(self, newvalue):
        if newvalue and not self.__is_app_being_held:
            self.hold()
            self.__is_app_being_held = True
        elif not newvalue and self.__is_app_being_held:
            self.release()
            self.__is_app_being_held = False

    @property
    def main_context(self):
        if not self.__main_context:
            from gi.repository import GLib
            self.__main_context = GLib.main_context_default()

        return self.__main_context

    def do_startup(self):
        """Default GTK method.

        Runs at application startup, to load
        any necessary UI elements.
        """
        logger.info(
            "\n"
            + "---------------------"
            + "----------------"
            + "------------\n\n"
            + "-----------\t"
            + "Initialized protonvpn"
            + "\t-----------\n\n"
            + "---------------------"
            + "----------------"
            + "------------"
        )
        logger.info(
            "Proton VPN v{} "
            "(protonvpn-nm-lib v{}; proton-client v{})".format(
                APP_VERSION, lib_version, proton_version
            )
        )
        if "SUDO_UID" in os.environ:
            logger.info("Initialized app with sudo")
            print(
                "\nRunning Proton VPN as root is not supported and "
                "is highly discouraged, as it might introduce "
                "undesirable side-effects."
            )
            user_input = input("Are you sure that you want to proceed (y/N): ")
            user_input = user_input.lower()
            if not user_input == "y":
                logger.info("Quit app as sudo")
                self.on_quit()

        Gtk.Application.do_startup(self)

        self.setup_actions()
        logger.info("Startup successful")

    def on_quit(self, *_):
        """On app quit event hanlder."""
        logger.info("Quit app")
        if protonvpn.get_active_protonvpn_connection():
            QuitDialog(self, self.quit_)
            return

        self.quit_()

    def quit_(self):
        try:
            protonvpn.disconnect()
        except exceptions.ConnectionNotFound:
            pass

        self.quit()

    def display_login_window(self, *_):
        self.is_logging_out = False
        self.get_login_window().display_view()

    def on_logout(self, *_):
        if self.is_logging_out:
            dialog = DisplayMessageDialog(
                application=self,
                title="Logout",
                description="You're currently being logged out, please wait..."
            )
            return

        self.hold_app = True

        self.is_logging_out = True
        dialog = DisplayMessageDialog(
            application=self,
            title="Logout",
            description="Logging out..."
        )
        p = BackgroundProcess.factory("gtask")
        p.setup(
            target=self._logout,
            callback=self.display_login_window,
        )

        if protonvpn.get_active_protonvpn_connection():
            dialog.close_dialog()
            LogoutDialog(self, p.start)
            return

        p.start()

    def _logout(self, *args):
        active_windows = self.get_windows()

        # stop background processes
        logger.info("Stopping background process")
        for win in active_windows:
            try:
                self.main_context.invoke_full(
                    GTKPriorityEnum.PRIORITY_DEFAULT.value, win.prepare_for_app_shutdown
                )
            except AttributeError:
                pass

        # logout
        logger.info("Logging out")
        try:
            protonvpn.logout()
        except (Exception, exceptions.ProtonVPNException) as e:
            logger.exception(e)

        # close windows
        logger.info("Closing all windows \"{}\"".format(active_windows))
        for win in active_windows:
            try:
                self.main_context.invoke_full(
                    GTKPriorityEnum.PRIORITY_DEFAULT.value, win.on_close_window, None, None, True
                )
            except AttributeError:
                self.main_context.invoke_full(GTKPriorityEnum.PRIORITY_DEFAULT.value, win.destroy)

    def on_click_about(self, simple_action, _):
        AboutDialog(self)

    def on_click_get_logs(self, simple_action, _):
        dialog = DisplayMessageDialog(
            self,
            title="Generating logs",
            description="Generating logs, please wait..."
        )
        process = BackgroundProcess.factory()
        process.setup(
            self._async_get_logs,
            None,
            None,
            None,
            dialog,
        )
        process.start()

    def _async_get_logs(self, dialog, _=None):
        bug_report = protonvpn.get_bug_report()

        try:
            bug_report.generate_logs()
        except Exception as e:
            logger.exception(e)
            self.main_context.invoke_full(
                GTKPriorityEnum.PRIORITY_DEFAULT.value,
                self.__dialog_updater,
                dialog,
                "Unable to generate logs",
                "\nUnable to generate logs: {}".format(e)
            )
            return

        try:
            bug_report.open_folder_with_logs()
        except Exception as e:
            logger.exception(e)
            self.main_context.invoke_full(
                GTKPriorityEnum.PRIORITY_DEFAULT.value,
                self.__dialog_updater,
                dialog,
                "Unable to generate logs" \
                "\nUnable to open file explorer with logs. " \
                "You can find the logs at ~/.cache/protonvpn/logs" # noqa
            )
            return

        self.main_context.invoke_full(GTKPriorityEnum.PRIORITY_DEFAULT.value, dialog.close_dialog)

    def __dialog_updater(self, dialog, title, description):
        dialog.update_dialog_content(title, description)

    def on_display_preferences(self, *args):
        """On app display preferences event hanlder."""
        logger.info("Display preferences")
        print("To-do")

    def do_activate(self, *_):
        """Default GTK method.

        Runs after app startup and before displaying any windows.
        """
        win = self.props.active_window
        if not self.indicator:
            self.indicator = generate_protonvpn_indicator(self)

        if not win:
            try:
                if not protonvpn.check_session_exists():
                    win = self.get_login_window()
                else:
                    win = self.get_dashboard_window()
            except exceptions.ProtonVPNException as e:
                DisplayMessageDialog(
                    application=self,
                    title="Error",
                    description=str(e),
                    callback_func=self.quit_
                )
                return

        logger.info("Window to display {}".format(win))
        win.display_view()

    def get_login_window(self):
        """Get login window.

        Returns:
            LoginView
        """
        return LoginView(
            application=self,
            dashboard_window=self.get_dashboard_window
        )

    def get_dashboard_window(self):
        """Get dashboard window.

        Returns:
            DashboardView
        """
        return DashboardView(application=self)

    def setup_actions(self):
        quit_app = Gio.SimpleAction.new("quit", None)
        quit_app.connect("activate", self.on_quit)
        self.add_action(quit_app)

        logout = Gio.SimpleAction.new("logout", None)
        logout.connect("activate", self.on_logout)
        self.add_action(logout)

        about_dialog = Gio.SimpleAction.new("about", None)
        about_dialog.connect("activate", self.on_click_about)
        self.add_action(about_dialog)

        get_logs = Gio.SimpleAction.new("get-logs", None)
        get_logs.connect("activate", self.on_click_get_logs)
        self.add_action(get_logs)

        # TO-DO: Implement preferences
        # display_preferences = Gio.SimpleAction.new("display_preferences", None)
        # display_preferences.connect("activate", self.on_display_preferences)
        # self.add_action(display_preferences)


def main():
    app = ProtonVPNGUI()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
