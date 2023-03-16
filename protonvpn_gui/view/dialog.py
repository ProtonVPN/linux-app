import os

import gi

gi.require_version("Gtk", "3.0")
try:
    gi.require_version("WebKit2", "4.1")
except (ImportError, ValueError):
    gi.require_version("WebKit2", "4.0")

from gi.repository import Gdk, Gio, Gtk
from gi.repository import WebKit2 as Webkit
from proton.constants import VERSION as api_version
from protonvpn_nm_lib.constants import APP_VERSION as lib_version

from ..constants import APP_VERSION, CSS_DIR_PATH, UI_DIR_PATH, protonvpn_logo
from ..logger import logger
from ..patterns.factory import WidgetFactory


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "dialog.ui"))
class DialogView(Gtk.ApplicationWindow):
    """
    Dialog view. GTK Composite object.

    Dialog object as composite to displays a dialog window which is context based.
    """
    __gtype_name__ = "DialogView"

    # Labels
    headerbar_label = Gtk.Template.Child()
    # Images/Icons
    headerbar_sign_icon = Gtk.Template.Child()
    # Containers
    dialog_container_grid = Gtk.Template.Child()

    def __init__(self, application):
        super().__init__(application=application)
        self.dummy_object = WidgetFactory.image("dummy")
        self.content_label = WidgetFactory.label("dialog_main_text")

        self.__generate_content_grid()
        self.__generate_bottom_buttons_grid()
        self.__attach_grids()

        protonvpn_headerbar_pixbuf = self.dummy_object\
            .create_icon_pixbuf_from_name(
                "protonvpn-sign.svg",
                width=50, height=50,
            )
        window_icon = self.dummy_object.create_icon_pixbuf_from_name(
            protonvpn_logo
        )
        self.headerbar_sign_icon.set_from_pixbuf(protonvpn_headerbar_pixbuf)
        self.set_icon(window_icon)

        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(
            os.path.join(CSS_DIR_PATH, "dialog.css")
        )
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def display_dialog(self):
        """Displays the dialog to the user."""
        self.present()

    def close_dialog(self, cancel_button=None):
        """Closes and destroys the dialog."""
        self.destroy()

    def add_extra_content(self, widget):
        """Add extra content to window.

        Args:
            widget: should be a container (GTK.Grid or Gtk.Box)
        """
        self.__content_grid.attach_bottom_next_to(
            widget,
            self.content_label.widget
        )

    def __generate_content_grid(self):
        """Generate grid with contextual information."""
        self.__content_grid = WidgetFactory.grid("dialog_content")
        self.__content_grid.attach(self.content_label.widget, 0, 0, 1, 1)

    def __generate_bottom_buttons_grid(self):
        """Generate grid with buttons."""
        self.__bottom_grid = WidgetFactory.grid("dialog_buttons")

        buttons_grid = WidgetFactory.grid("dialog_buttons")
        buttons_grid.add_class("grid-button-spacing")
        buttons_grid.align_h = Gtk.Align.END
        buttons_grid.align_v = Gtk.Align.CENTER
        buttons_grid.expand_h = True
        buttons_grid.column_spacing = 15

        self.main_button = WidgetFactory.button("dialog_main")
        self.cancel_button = WidgetFactory.button("dialog_close")

        buttons_grid.attach(self.cancel_button.widget, 0, 0, 1, 1)
        buttons_grid.attach_next_to(
            self.main_button.widget, self.cancel_button.widget,
            Gtk.PositionType.RIGHT, 1, 1
        )
        self.__bottom_grid.attach(buttons_grid.widget, 0, 0, 1, 1)
        self.cancel_button.connect("clicked", self.close_dialog)

    def __attach_grids(self):
        """Attach custom content to dialog content grid."""
        self.dialog_container_grid.attach(self.__content_grid.widget, 0, 0, 1, 1)
        self.dialog_container_grid.attach_next_to(
            self.__bottom_grid.widget, self.__content_grid.widget,
            Gtk.PositionType.BOTTOM, 1, 1
        )

    def add_class(self, css_style):
        style_context = self.dialog_container_grid.get_style_context()
        style_context.add_class(css_style)

    @property
    def buttons_visible(self):
        return self.__bottom_grid.show

    @buttons_visible.setter
    def buttons_visible(self, newvalue):
        self.__bottom_grid.show = newvalue


class LoginKillSwitchDialog:
    """Login Kill Switch Dialog.

    Is displayed when the users clicks on disable button on login
    screen. The button that displays this dialog will only appear
    if the user is not logged in and the kill switch is detected as enabled.
    """
    def __init__(
        self, application, login_view_model, callback_func=None
    ):
        self.login_view_model = login_view_model
        self.dialog_view = DialogView(application)
        self.dialog_view.headerbar_label.set_text("Disable Kill Switch")
        self.dialog_view.content_label.content = "Permanent Kill Switch is " \
            "blocking any outgoing connection and preventing " \
            "your IP to be exposed.\n\n" \
            "Do you want to disable Kill Switch ?"

        self.dialog_view.main_button.connect(
            "clicked", self.on_click_disable_killswitch,
            callback_func, application
        )
        self.dialog_view.main_button.label = "Disable"
        self.dialog_view.display_dialog()

    def on_click_disable_killswitch(self, continue_button, callback_func, application):
        self.login_view_model.disable_killswitch()
        callback_func()
        self.dialog_view.close_dialog()


class ConnectUpgradeDialog:
    """Connect Upgrade Dialog.

    Is displayed when the users clicks on upgrade button on server
    objects. The button that displays this dialog will only appear
    if the the server tier is higher when compared to users tier.
    """
    def __init__(self, application, callback_func=None):
        self.dialog_view = DialogView(application)
        self.dialog_view.headerbar_label.set_text("Upgrade required")
        self.dialog_view.content_label.content = "You're trying to connect " \
            "to a server which requires " \
            "a Proton VPN Plus Subscription or higher." \
            "\n\nTo access more servers in all countries, please " \
            "upgrade your subscription."

        self.dialog_view.main_button.connect(
            "clicked", self.on_click_upgrade_account, callback_func
        )
        self.dialog_view.main_button.label = "Upgrade"
        self.dialog_view.display_dialog()

    def on_click_upgrade_account(self, main_button, callback_func):
        """Open window in browser with the specified URI to upgrade account."""
        Gtk.show_uri_on_window(
            None,
            "https://account.protonvpn.com/",
            Gdk.CURRENT_TIME
        )
        self.dialog_view.close_dialog()


class LogoutDialog:
    """Logout Dialog.

    Is displayed when the users clicks on logout button.
    """
    def __init__(self, application, callback_func=None):
        self.dialog_view = DialogView(application)
        self.dialog_view.headerbar_label.set_text("VPN Connection Active")
        self.dialog_view.content_label.content = "Logging out of the " \
            "application will disconnect the active VPN connection.\n\n" \
            "Do you want to continue ?"

        self.dialog_view.main_button.connect(
            "clicked", self.on_click_logout, callback_func
        )
        self.dialog_view.main_button.label = "Continue"
        self.dialog_view.display_dialog()

    def on_click_logout(self, main_button, callback_func):
        """Call logout callback."""
        self.dialog_view.content_label.content = "Please wait while you're " \
            "being logged out..."
        self.dialog_view.main_button.show = False
        callback_func()


class QuitDialog:
    """Quit Dialog.

    Is displayed when the users clicks on quit button.
    """
    def __init__(self, application, callback_func=None):
        self.dialog_view = DialogView(application)
        self.dialog_view.headerbar_label.set_text("VPN Connection Active")
        self.dialog_view.content_label.content = "Quitting the application " \
            "will disconnnect the active VPN connection.\n\n" \
            "Do you want to continue ?"

        self.dialog_view.main_button.connect(
            "clicked", self.on_click_quit, callback_func
        )
        self.dialog_view.main_button.label = "Continue"
        self.dialog_view.display_dialog()

    def on_click_quit(self, main_button, callback_func):
        """Call logout callback."""
        callback_func()


class AboutDialog:
    """About Dialog.

    Is displayed when the users clicks on logout button.
    """
    def __init__(self, application, callback_func=None):
        import datetime
        self.dialog_view = DialogView(application)
        self.dialog_view.headerbar_label.set_text("About")
        app_version = "Proton VPN: \tv{} (library: v{} / api-client: v{})".format(
            APP_VERSION, lib_version, api_version
        )
        self.dialog_view.content_label.align_h = Gtk.Align.START
        self.dialog_view.content_label.ident_h = 0
        self.dialog_view.content_label.content = app_version
        self.dialog_view.content_label.can_be_selected = True
        self.dialog_view.content_label.can_focus = False
        self.dialog_view.buttons_visible = False
        additional_context = WidgetFactory.grid("default")
        copyright_label = WidgetFactory.label(
            "default", "Copyright Proton AG {}".format(datetime.datetime.now().date().strftime("%Y"))
        )
        copyright_label.add_class("text-weak")
        copyright_label.add_class("font-small")
        additional_context.attach(copyright_label.widget)
        additional_context.ident_h = 0
        additional_context.ident_v = 0
        copyright_label.ident_h = 0
        copyright_label.ident_v = 0
        self.dialog_view.add_extra_content(additional_context.widget)

        self.dialog_view.display_dialog()


class DisplayMessageDialog:
    """Display message dialog

    This dialog can be used whenever a message should be displayed to the user.
    """
    def __init__(self, application, callback_func=None, title=None, description=None):
        self.dialog_view = DialogView(application)
        self.dialog_view.headerbar_label.set_text(title if title else "Information")
        self.dialog_view.content_label.content = \
            description if description else "No additional context was provided."
        self.dialog_view.buttons_visible = False

        self.dialog_view.display_dialog()
        self.dialog_view.connect("destroy", self.close_dialog, callback_func)

    def close_dialog(self, dialog_view=None, callback_func=None):
        self.dialog_view.close_dialog()
        if callback_func:
            callback_func()

    def update_dialog_content(self, title=None, desc=None):
        if title:
            self.dialog_view.headerbar_label.set_text(title)

        if desc:
            self.dialog_view.content_label.content = desc


class WebView:
    """Display message dialog

    This dialog can be used whenever a message should be displayed to the user.
    """
    def __init__(self, application, callback_func=None, title=None, description=None):
        self.__callback = callback_func
        self.__dialog_view = DialogView(application)
        self.__dialog_view.headerbar_label.set_text(title if title else "Proton VPN Captcha")
        self.__dialog_view.content_label.show = False
        self.__dialog_view.buttons_visible = False
        self.__dialog_view.add_class("no-margin")
        self.__default_webview_height = 100

        # WebView
        # https://lazka.github.io/pgi-docs/#WebKit2-4.0/classes/UserContentManager.html#WebKit2.UserContentManager.register_script_message_handler
        # https://lazka.github.io/pgi-docs/index.html#WebKit2-4.0/classes/WebView.html#WebKit2.WebView.new_with_user_content_manager
        # https://stackoverflow.com/questions/63109260/how-to-connect-javascript-and-python-using-webkit2gtk

        content_manager = Webkit.UserContentManager.new()
        content_manager.connect(
            "script-message-received::linuxWebkitWebview",
            self.receive_post_message
        )

        if not content_manager.register_script_message_handler("linuxWebkitWebview"):
            logger.error("Unable to register script message handler")
            raise Exception("Unable to register script message handler")

        logger.info("registered script message handler")

        self.__webview = Webkit.WebView.new_with_user_content_manager(content_manager)

        self.__webview.set_property("expand", True)
        self.__webview.set_property("height-request", self.__default_webview_height)
        self.__webview.set_property("width-request", self.__dialog_view.get_size()[0] + 10)

        # ## Can be helpfull during debugging
        # settings = self.__webview.get_settings()
        # settings.set_enable_developer_extras(True)
        # settings.set_allow_top_navigation_to_data_urls(True)
        # settings.set_enable_frame_flattening(True)
        # self.__webview.set_settings(settings)

        self.__dialog_view.add_extra_content(self.__webview)

    def display(self, url):
        self.__webview.set_property("visible", True)
        self.__webview.load_uri(url)
        self.__dialog_view.display_dialog()

    def receive_post_message(self, user_content_manager, js_result):
        import json
        response = json.loads(js_result.get_js_value().to_json(0))
        if response.get("type") == "pm_height":
            height = response.get("height", self.__default_webview_height)
            self.__webview.set_property("height-request", height)
        elif response.get("type") == "pm_captcha":
            self.__callback(captcha=("captcha", response.get("token")))
            self.__dialog_view.close_dialog()


class TroubleshootDialog:
    """Display troubleshoot dialog."""
    def __init__(self, application, callback_func=None):
        self.__dialog_view = DialogView(application)
        self.__dialog_view.headerbar_label.set_text("Troubleshooting")
        self.__dialog_view.content_label.show = False
        self.__dialog_view.buttons_visible = False
        self.__row_counter = 0

        self.__additional_context = WidgetFactory.grid("troubleshoot_container")
        self.__alt_routing_widget()
        self.__no_connection_widget()
        self.__isp_problem_widget()
        self.__gov_block_widget()
        self.__antivirus_widget()
        self.__proxy_firewall_widget()
        self.__proton_is_down_widget()
        self.__no_solution_widget()
        self.__dialog_view.add_extra_content(self.__additional_context.widget)

        self.__dialog_view.display_dialog()

    def __alt_routing_widget(self):
        title = "Allow Alternative Routing"
        description = "In case Proton sites are blocked, " \
            "this setting allows the app to try alternative network " \
            "routing to reach Proton, which can be useful for bypassing " \
            "firewalls or network issues. We recommend keeping this "\
            "setting on for greater reliability. "
        learn_more = "Learn more"

        description = WidgetFactory.textview("default", description)
        description.insert_link_at_end(
            learn_more,
            "https://protonmail.com/blog/anti-censorship-alternative-routing",
            self._open_url
        )

        self.__generate_widget(title, description, True)

    def __no_connection_widget(self):
        title = "No internet connection"
        _description = "Please make sure that your internet connection " \
            "is working."
        description = WidgetFactory.textview("default", _description)

        self.__generate_widget(title, description)

    def __isp_problem_widget(self):
        title = "Internet Service Provider (ISP) problem"
        _description = "Try connecting to Proton from a different network " \
            "(or use "
        _end = ")."
        description = WidgetFactory.textview("default", _description)
        description.insert_link_at_end("Tor", "https://www.torproject.org", self._open_url)
        description.inset_text_at_end(_end)
        self.__generate_widget(title, description)

    def __gov_block_widget(self):
        title = "Government block"
        _description = "Your country may be blocking access to Proton. " \
            "Try using "
        _end = " to access Proton."
        description = WidgetFactory.textview("default", _description)
        description.insert_link_at_end("Tor", "https://www.torproject.org", self._open_url)
        description.inset_text_at_end(_end)

        self.__generate_widget(title, description)

    def __antivirus_widget(self):
        title = "Antivirus interference"
        _description = "Temporarly disable or remove your antivirus software."
        description = WidgetFactory.textview("default", _description)

        self.__generate_widget(title, description)

    def __proxy_firewall_widget(self):
        title = "Proxy/Firewall interference"
        _description = "Disable any proxies or firewalls, or contact your " \
            "network administrator."
        description = WidgetFactory.textview("default", _description)

        self.__generate_widget(title, description)

    def __proton_is_down_widget(self):
        title = "Proton is down"
        _description = "Check "
        _end = " for our system status."
        description = WidgetFactory.textview("default", _description)
        description.insert_link_at_end("Proton Status", "https://protonstatus.com", self._open_url)
        description.inset_text_at_end(_end)

        self.__generate_widget(title, description)

    def __no_solution_widget(self):
        title = "Still can't find a solution"
        _description = "Contact us directly through our "
        _middle = ", "
        _end = " or "
        description = WidgetFactory.textview("default", _description)
        description.insert_link_at_end(
            "support form", "https://protonvpn.com/support-form", self._open_url
        )
        description.inset_text_at_end(_middle)
        description.insert_link_at_end(
            "email (support@protonmail.com)", "mailto:support@protonvpn.com", self._open_url
        )
        description.inset_text_at_end(_end)
        description.insert_link_at_end("Twitter.", "https://twitter.com/ProtonVPN", self._open_url)

        self.__generate_widget(title, description)

    def __generate_widget(self, _title, description, add_switch=False):
        """Generate widget.

        Args:
            _title (string): row title
            description (TextViewFactory): (Gtk.TextView)
        """
        _grid = WidgetFactory.grid("default")
        title = WidgetFactory.label("troubleshoot_title", _title)

        # Attach content to individual grid
        _grid.attach(title.widget)
        _grid.attach_bottom_next_to(description.widget, title.widget)

        if add_switch:
            from protonvpn_nm_lib.api import protonvpn
            from protonvpn_nm_lib.enums import UserSettingStatusEnum

            _grid.column_spacing = 40
            alt_routing_switch = WidgetFactory.switch("troubleshoot_dialog")
            if protonvpn.get_settings().alternative_routing == UserSettingStatusEnum.ENABLED:
                alt_routing_switch.is_active = True
            else:
                alt_routing_switch.is_active = False

            alt_routing_switch.widget.connect("notify::active", self.__update_alternative_routing)
            _grid.attach_right_next_to(alt_routing_switch.widget, title.widget, height=2)

        # Attach to main grid
        if not self.__row_counter:
            self.__additional_context.attach(_grid.widget)
            self.__row_counter += 1
            return

        self.__additional_context.attach(_grid.widget, row=self.__row_counter)
        self.__row_counter += 1

    def __update_alternative_routing(self, switch, state):
        from protonvpn_nm_lib.api import protonvpn
        from protonvpn_nm_lib.enums import UserSettingStatusEnum

        try:
            protonvpn.get_settings().alternative_routing = UserSettingStatusEnum(
                int(switch.get_state())
            )
        except Exception as e:
            logger.exception(e)

    def _open_url(self, tag, textview, gdk_event, textiter, url):
        if gdk_event.get_event_type() == Gdk.EventType.BUTTON_RELEASE:
            _ = Gio.AppInfo.launch_default_for_uri(url)


class GenericEventDialog:
    def __init__(self, application, generic_event):
        dialog_view = DialogView(application)
        dialog_view.headerbar_label.set_text(generic_event.label)
        dialog_view.content_label.show = False
        dialog_view.buttons_visible = False

        additional_context = WidgetFactory.grid("dashboard_event_main_grid")
        top_grid = self.__generate_top_content(generic_event)
        mid_grid = self.__generate_mid_content(generic_event)
        bottom_grid = self.__generate_bottom_content(generic_event)

        additional_context.attach(top_grid.widget)
        additional_context.attach_bottom_next_to(mid_grid.widget, top_grid.widget)
        additional_context.attach_bottom_next_to(bottom_grid.widget, mid_grid.widget)

        dialog_view.add_extra_content(additional_context.widget)

        dialog_view.display_dialog()

    def __generate_top_content(self, generic_event):
        content_grid = WidgetFactory.grid("dashboard_event_top_grid")

        _incentive = generic_event.incentive
        if not _incentive:
            _incentive = "None"

        incentive_text = _incentive[0:generic_event.incentive_template_index_start - 1]
        incentive_price = _incentive[generic_event.incentive_template_index_start:len(_incentive)]

        incentive_price = incentive_price.replace(
            "%IncentivePrice%",
            "<span size=\"x-large\" weight=\"bold\">{}</span>".format(
                generic_event.incentive_price
            )
        )
        incentive = "<span size=\"medium\">{}</span> {}".format(incentive_text, incentive_price)

        upgrade_to_label = WidgetFactory.label("generic_event_incentive")
        upgrade_to_label.set_content_with_markup(incentive)

        save_up_to_label = WidgetFactory.label("generic_event_save_up_to", generic_event.pill)

        content_grid.attach(upgrade_to_label.widget)
        content_grid.attach_bottom_next_to(save_up_to_label.widget, upgrade_to_label.widget)

        return content_grid

    def __generate_mid_content(self, generic_event):
        import re
        pattern = re.compile(r"[\/]{1}([a-zA-Z0-9-]+\.(png|jpeg|jpg))")
        pattern_result = pattern.search(generic_event.picture_url)

        icon_path = \
            self.__get_icon_path(pattern_result.group(1)) \
            if pattern_result \
            else None

        content_grid = WidgetFactory.grid("dashboard_event_mid_grid")
        gift_box = WidgetFactory.image("dashboard_event_main_icon", icon_path)
        title = WidgetFactory.label("generic_event_title")
        title.set_content_with_markup(
            "<span font_weight=\"heavy\" size=\"large\">{}</span>".format(
                generic_event.title
            )
        )

        content_grid.attach(gift_box.widget)
        content_grid.attach_bottom_next_to(title.widget, gift_box.widget)

        features_holder_grid = self.__generate_features_list(generic_event.features, pattern)
        content_grid.attach_bottom_next_to(features_holder_grid.widget, title.widget)
        return content_grid

    def __generate_features_list(self, generic_event_features, pattern):
        features_holder_grid = WidgetFactory.grid("generic_event_features_holder_grid")
        previous_feature_grid = None

        for text, icon_url in generic_event_features:
            feature_grid = WidgetFactory.grid("generic_event_feature_grid")
            pattern_result = pattern.search(icon_url)
            icon = WidgetFactory.image(
                "dashboard_event_icon",
                self.__get_icon_path(pattern_result.group(1))
            ) if pattern_result else WidgetFactory.image("dummy")

            label = WidgetFactory.label("default", text)

            # Add icon and text to feature grid
            feature_grid.attach(icon.widget)
            feature_grid.attach_right_next_to(label.widget, icon.widget)

            # Check if there is a previous feature grid, if yes then attach below it
            if not previous_feature_grid:
                features_holder_grid.attach(feature_grid.widget)
            else:
                features_holder_grid.attach_bottom_next_to(
                    feature_grid.widget, previous_feature_grid.widget
                )

            previous_feature_grid = feature_grid

        return features_holder_grid

    def __get_icon_path(self, icon_name):
        import os
        from protonvpn_nm_lib.constants import PROTON_XDG_CACHE_HOME_NOTIFICATION_ICONS

        return os.path.join(PROTON_XDG_CACHE_HOME_NOTIFICATION_ICONS, icon_name)

    def __generate_bottom_content(self, generic_event):
        content_grid = WidgetFactory.grid("dashboard_event_bottom_grid")
        button = WidgetFactory.button("dialog_main")
        button.label = generic_event.button_text
        under_text = WidgetFactory.label("generic_event_footer")
        under_text.set_content_with_markup(
            "<span size=\"small\">{}</span>".format(generic_event.page_footer)
        )

        button.connect("clicked", self._open_url, generic_event.button_url)

        content_grid.attach(button.widget)
        content_grid.attach_bottom_next_to(under_text.widget, button.widget)

        return content_grid

    def _open_url(self, gtk_button, url):
        _ = Gio.AppInfo.launch_default_for_uri(url)


class WelomeToNewBrandDialog:
    """This dialog is only showed once due to rebranding"""
    def __init__(self, application, callback_func=None):
        dialog_view = DialogView(application)
        dialog_view.content_label.show = False
        dialog_view.buttons_visible = False

        additional_context = WidgetFactory.grid("dashboard_event_main_grid")
        top_grid = self.__generate_top_content()
        mid_grid = self.__generate_mid_content()
        bottom_grid = self.__generate_bottom_content(callback_func, dialog_view)

        additional_context.attach(top_grid.widget)
        additional_context.attach_bottom_next_to(mid_grid.widget, top_grid.widget)
        additional_context.attach_bottom_next_to(bottom_grid.widget, mid_grid.widget)

        dialog_view.add_extra_content(additional_context.widget)

        dialog_view.display_dialog()

    def __generate_top_content(self):
        grid = WidgetFactory.grid("default")
        grid.align_h = Gtk.Align.CENTER

        new_branch_bg = WidgetFactory.image("new-brand-bg")
        grid.attach(new_branch_bg.widget)

        return grid

    def __generate_mid_content(self):
        grid = WidgetFactory.grid("default")
        grid.align_h = Gtk.Align.CENTER
        grid.add_class("margin-y-30px")

        text1 = WidgetFactory.label("new-brand-title", "Updated Proton, unified protection")
        text2 = WidgetFactory.textview(
            "new-brand",
            "Introducing Proton's refreshed look. Many services, one "\
            "mission. Welcome to an Internet where privacy is the default."
        )
        button = WidgetFactory.button("learn-more-aligned-center")
        button.url = "https://protonvpn.com/blog/updated-proton-vpn"
        button.label = "Learn more"

        text1.add_class("default-text-view")
        text2.add_class("default-text-view")
        text2.add_class("margin-top-10px")
        text1.show = True
        text2.show = True
        button.show = True

        grid.attach(text1.widget)
        grid.attach_bottom_next_to(text2.widget, text1.widget)
        grid.attach_bottom_next_to(button.widget, text2.widget)

        return grid

    def __generate_bottom_content(self, callback_func, dialog_view):
        grid = WidgetFactory.grid("default")
        grid.align_h = Gtk.Align.CENTER
        grid.row_spacing = 35
        grid.column_spacing = 20

        button = WidgetFactory.button("dialog_main")
        button.label = "Got it"
        button.align_h = Gtk.Align.CENTER
        button.connect("clicked", self.__on_click, callback_func, dialog_view.close_dialog)

        mail_icon = WidgetFactory.image("small-mail-logo")
        calendar_icon = WidgetFactory.image("small-calendar-logo")
        drive_icon = WidgetFactory.image("small-drive-logo")
        vpn_icon = WidgetFactory.image("small-vpn-logo")

        grid.attach(button.widget, width=4)
        grid.attach_bottom_next_to(mail_icon.widget, button.widget)
        grid.attach_right_next_to(calendar_icon.widget, mail_icon.widget)
        grid.attach_right_next_to(drive_icon.widget, calendar_icon.widget)
        grid.attach_right_next_to(vpn_icon.widget, drive_icon.widget)

        return grid

    def __on_click(self, button, callback_func, close_dialog):
        callback_func()
        close_dialog()
