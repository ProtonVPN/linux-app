import os

import gi

gi.require_version('Gtk', '3.0')

import weakref

from gi.repository import Gdk, Gio, GLib, Gtk

from ..constants import (CSS_DIR_PATH, KILLSWITCH_ICON_SET, NETSHIELD_ICON_SET,
                         SECURE_CORE_ICON_SET, UI_DIR_PATH, protonvpn_logo)
from ..enums import (DashboardFeaturesEnum, GLibEventSourceEnum,
                     IndicatorActionEnum)
from ..logger import logger
from ..module import Module
from ..patterns.factory import WidgetFactory
from ..view_model.dataclass.dashboard import (ConnectedToVPNInfo, ConnectError,
                                              ConnectInProgressInfo,
                                              ConnectPreparingInfo,
                                              DisplayDialog, DisplayEvent,
                                              Loading, NetworkSpeed,
                                              NotConnectedToVPNInfo,
                                              QuickSettingsStatus)
from .dashboard_states import (ConnectedVPNView, ConnectVPNErrorView,
                               ConnectVPNInProgressView,
                               ConnectVPNPreparingView, EventNotification,
                               InitLoadView, NotConnectedVPNView,
                               UpdateNetworkSpeedView, UpdateQuickSettings)
from .dialog import DisplayMessageDialog, TroubleshootDialog
from .quick_settings_popover import QuickSettingsPopoverView
from .server_list import ServerListView


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "dashboard.ui"))
class DashboardView(Gtk.ApplicationWindow):
    """
    Dashboard view. GTK Composite object.

    Renders everything related to the user Dashboard. It's different
    views are managed by the listener dashboard_view_model.state,
    which is updated once certain operations are concluded in the ViewModel.

    Different view types are rendered in the method render_view_state, which
    attempts to match the instance state defined in dashboard_view_model.
    The view types are divided into own classes which receive the current
    instance of DashboardView and the proceed to manipulate the UI. Creating
    new classes was preferred instead of methods to facilitate code reading
    and clear separation of view states.


    Once connections are started or ended, the UI will react accordingly.
    Also, background processes started with Glib.timeout_add_seconds are
    constantly monitored and tracked to make sure that there are no
    multiple background similar processes running at the same time.
    Ie: Two existing processes which update the network speed each second.
    """
    __gtype_name__ = 'DashboardView'

    # UI Constants - Other objects
    headerbar = Gtk.Template.Child()

    overlay_spinner = Gtk.Template.Child()
    connecting_overlay_spinner = Gtk.Template.Child()
    connecting_progress_bar = Gtk.Template.Child()

    server_list_scrolled_window = Gtk.Template.Child()
    server_list_view_port = Gtk.Template.Child()

    # UI Constants - Popover menus
    dashboard_popover_menu = Gtk.Template.Child()

    # UI Constants - Buttons
    # The button below is not used and is left only for
    # reference that it exists and can be used if wished.
    # headerbar_menu_button = Gtk.Template.Child()
    quick_connect_button = Gtk.Template.Child()
    main_disconnect_button = Gtk.Template.Child()
    cancel_connect_overlay_button = Gtk.Template.Child()
    dashboard_secure_core_button_menu = Gtk.Template.Child()
    dashboard_netshield_button = Gtk.Template.Child()
    dashboard_killswitch_button = Gtk.Template.Child()
    server_search_entry = Gtk.Template.Child()
    servers_info_icon_button = Gtk.Template.Child()

    # UI Constants - Labels
    country_servername_label = Gtk.Template.Child()
    ip_label = Gtk.Template.Child()
    serverload_label = Gtk.Template.Child()
    download_speed_label = Gtk.Template.Child()
    connected_protocol_label = Gtk.Template.Child()
    upload_speed_label = Gtk.Template.Child()
    locations_label = Gtk.Template.Child()
    overlay_bottom_label = Gtk.Template.Child()
    connecting_to_label = Gtk.Template.Child()

    # UI Constants - Images/Icons
    headerbar_sign_icon = Gtk.Template.Child()
    overlay_logo_image = Gtk.Template.Child()
    server_load_image = Gtk.Template.Child()
    download_speed_image = Gtk.Template.Child()
    upload_speed_image = Gtk.Template.Child()
    servers_info_icon = Gtk.Template.Child()
    sidebar_country_image = Gtk.Template.Child()
    dashboard_secure_core_button_image = Gtk.Template.Child()
    dashboard_netshield_button_image = Gtk.Template.Child()
    dashboard_killswitch_button_image = Gtk.Template.Child()

    # UI Constants - Grids
    connected_label_grid = Gtk.Template.Child()
    ip_label_grid = Gtk.Template.Child()
    ip_server_load_labels_grid = Gtk.Template.Child()
    connection_information_grid = Gtk.Template.Child()
    connection_speed_label_grid = Gtk.Template.Child()
    top_sever_locations_grid = Gtk.Template.Child()
    server_list_grid = Gtk.Template.Child()

    # UI Constants - Boxes
    overlay_box = Gtk.Template.Child()
    connecting_overlay_box = Gtk.Template.Child()

    # UI Updates in seconds constants
    on_network_speed_update_seconds = 1
    on_vpn_monitor_update_seconds = 3
    on_server_load_update_seconds = 900  # every 15min
    on_event_update_seconds = 720  # every 12min

    # Other Constants
    feature_button_icon_width = 20
    feature_button_icon_height = 20

    glib_source_tracker = {
        GLibEventSourceEnum.ON_MONITOR_VPN: None,
        GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED: None,
        GLibEventSourceEnum.ON_SERVER_LOAD: None,
        GLibEventSourceEnum.ON_EVENT: None,
    }
    glib_source_updated_time = {
        GLibEventSourceEnum.ON_MONITOR_VPN:
            on_vpn_monitor_update_seconds,
        GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED:
            on_network_speed_update_seconds,
        GLibEventSourceEnum.ON_SERVER_LOAD:
            on_server_load_update_seconds,
        GLibEventSourceEnum.ON_EVENT:
            on_event_update_seconds
    }

    features_icon_set_dict = {
        DashboardFeaturesEnum.KILLSWITCH: KILLSWITCH_ICON_SET,
        DashboardFeaturesEnum.NETSHIELD: NETSHIELD_ICON_SET,
        DashboardFeaturesEnum.SECURE_CORE: SECURE_CORE_ICON_SET
    }

    def __init__(self, **kwargs):
        self.application = kwargs.pop("application")
        super().__init__(application=self.application)

        self.setup_properties()
        self.set_windows_resize_restrictions()
        self.setup_icons_images()
        self.setup_css()
        self.setup_actions()
        self._preload_ui_resources()

    def display_view(self):
        self.render_view_state(Loading())
        self.present()

    def _preload_ui_resources(self):
        self.dashboard_view_model.on_startup_preload_resources_async()

    def indicator_action(self, indicator_state):
        if indicator_state == IndicatorActionEnum.QUICK_CONNECT:
            self.on_click_quick_connect(None, None)
        elif indicator_state == IndicatorActionEnum.DISCONNECT:
            self.on_click_disconnect(None, None)
        elif indicator_state == IndicatorActionEnum.SHOW_GUI:
            self.set_visible(True)
        else:
            logger.info("Invalid indicator state \"{}\"".format(indicator_state))

    def render_view_state(self, state):
        """Render view state.

        State is continuously being monitored. The state monitor is
        initialized in the __init__ method.
        Based on each instance, it will call a specific class, passing
        the instance of this current object and the state, so that the
        UI can be updated accordingly.
        """
        if isinstance(state, Loading):
            InitLoadView(self, state)
        elif isinstance(state, NotConnectedToVPNInfo):
            NotConnectedVPNView(self, state)
        elif isinstance(state, ConnectPreparingInfo):
            ConnectVPNPreparingView(self, state)
        elif isinstance(state, ConnectInProgressInfo):
            ConnectVPNInProgressView(self, state)
        elif isinstance(state, ConnectedToVPNInfo):
            ConnectedVPNView(self, state)
        elif isinstance(state, ConnectError):
            ConnectVPNErrorView(self, state)
            if state.display_troubleshoot_dialog:
                TroubleshootDialog(self.application)
        elif isinstance(state, NetworkSpeed):
            UpdateNetworkSpeedView(self, state)
        elif isinstance(state, QuickSettingsStatus):
            UpdateQuickSettings(self, state)
        elif isinstance(state, DisplayEvent):
            EventNotification(self, state)
        elif isinstance(state, DisplayDialog):
            DisplayMessageDialog(
                self.application,
                title=state.title,
                description=state.text
            )

    def on_click_disconnect(self, gkt_simple_action, _):
        """On click on Disconnect event handler.

        Disconnects from VPN.

        Args:
            gtk_button_object (Gtk.Button)

        """
        logger.info("Clicked on disconnect.")
        self.remove_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        self.remove_background_glib(
            GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED
        )
        self.main_disconnect_button.props.sensitive = False
        self.dashboard_view_model.on_disconnect()

    def on_click_quick_connect(self, gkt_simple_action, _):
        """On click Quick Connect event handler.

        Quickly connect to a VPN server.

        Args:
            gtk_button_object (Gtk.Button)
        """
        logger.info("Clicked on quick connect.")
        self.remove_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        self.quick_connect_button.props.sensitive = False
        self.dashboard_view_model.on_quick_connect()

    def on_click_hide_connect_overlay(
        self, gtk_button_object, gio_task_object
    ):
        """On click hides connect overlay.

        If a user attempts to connect to VPN but it fails for some reason,
        the UI is updated accordingly with the message and a close button is
        displayed to the user so that it can close the window and attempt to
        connect again or do other things.
        """
        self.gtk_property_setter(self.SET_UI_NOT_CONNECTED)

    def on_connect_load_sidebar_flag(self, country_code):
        """Loads sidebar flag on connect.

        Loads corresponding country flag to the country.
        Since the ViewModel returns a server object,
        we can easily access the country code.

        If it finds a matching country, it will setup the country
        flag, else it will just return without any errors.

        Args:
            country_code (string): country IS code
        """
        try:
            _dummy_object = WidgetFactory.image("dummy")
            dummy_object = weakref.proxy(_dummy_object)
            sidebar_flag_pixbuff = dummy_object.create_image_pixbuf_from_name(
                "flags/large/" + country_code.lower() + ".jpg",
                width=400, height=400,
            )
        except gi.repository.GLib.Error:
            return

        self.sidebar_country_image.set_from_pixbuf(sidebar_flag_pixbuff)

    def on_display_main_popover_menu(self, gio_simple_action, _):
        """On display main popover event handler.

        Displays top menu popover.

        Args:
            gio_simple_action(Gtk.Action)

        """
        self.dashboard_popover_menu.popup()

    def setup_properties(self):
        # ViewModel
        self.dashboard_view_model = Module().dashboard_view_model
        self.dashboard_view_model.gtk_app = self.application
        self.dashboard_view_model.state.subscribe(
            lambda state: GLib.idle_add(self.render_view_state, state)
        )

        # Indicator
        self.application.indicator.setup_reply_subject()
        try:
            self.application.indicator.dashboard_action.subscribe(
                lambda indicator_state: self.indicator_action(indicator_state)
            )
        except AttributeError:
            pass

        # Other views
        self.server_list_view = ServerListView(weakref.proxy(self))
        self.quick_settings_popover = QuickSettingsPopoverView(
            weakref.proxy(self.dashboard_view_model)
        )
        self.event_notification = None

        # Other UI properties
        self.overlay_spinner.set_property("width-request", 200)
        self.overlay_spinner.set_property("height-request", 200)
        self.connecting_overlay_spinner.set_property("width-request", 200)
        self.connecting_overlay_spinner.set_property("height-request", 200)
        self.SET_UI_NOT_CONNECTED = {
            "property": "visible",
            "objects": [
                (self.download_speed_label, False),
                (self.download_speed_image, False),
                (self.upload_speed_image, False),
                (self.upload_speed_label, False),
                (self.serverload_label, False),
                (self.sidebar_country_image, False),
                (self.server_load_image, False),
                (self.connecting_overlay_box, False),
                (self.overlay_box, False),
            ]
        }
        self.SET_UI_CONNECTED = {
            "property": "visible",
            "objects": [
                (self.download_speed_label, True),
                (self.download_speed_image, True),
                (self.upload_speed_image, True),
                (self.upload_speed_label, True),
                (self.serverload_label, True),
                (self.sidebar_country_image, True),
                (self.server_load_image, False),
                (self.connecting_overlay_box, False),
                (self.overlay_box, False),
            ]
        }
        self.overlay_box_context = self.overlay_box.get_style_context()
        self.glib_source_updated_method = {
            GLibEventSourceEnum.ON_MONITOR_VPN:
                self.dashboard_view_model.on_monitor_vpn_async,
            GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED:
                self.dashboard_view_model.on_update_speed_async,
            GLibEventSourceEnum.ON_SERVER_LOAD:
                self.dashboard_view_model.on_update_server_load,
            GLibEventSourceEnum.ON_EVENT:
                self.dashboard_view_model.async_check_if_events_should_be_displayed
        }

    def set_windows_resize_restrictions(self):
        geometry = Gdk.Geometry()
        geometry.min_width = 0
        geometry.max_width = self.get_default_size().width
        geometry.min_height = 0
        geometry.max_height = 99999
        self.set_geometry_hints(
            self,
            geometry,
            (Gdk.WindowHints.MIN_SIZE | Gdk.WindowHints.MAX_SIZE)
        )

    def setup_icons_images(self):
        """Sets up all icons and images at application start.

        All icons and images that need to be loaded and setup
        on window start are managed here. With the only exception
        of the sidebar flag.
        """
        logger.info("Setting up dashboard images and icons")
        _dummy_object = WidgetFactory.image("dummy")
        dummy_object = weakref.proxy(_dummy_object)

        # Get pixbuf objects
        protonvpn_headerbar_pixbuf = dummy_object.create_icon_pixbuf_from_name(
            "protonvpn-sign.svg",
            width=50, height=50,
        )
        logo_pixbuf = dummy_object.create_image_pixbuf_from_name(
            "protonvpn-logo.svg",
            width=325, height=250
        )
        window_icon = dummy_object.create_icon_pixbuf_from_name(
            protonvpn_logo
        )
        upload_pixbuff = dummy_object.create_icon_pixbuf_from_name(
            "up-icon.svg",
            width=15, height=15
        )
        download_pixbuff = dummy_object.create_icon_pixbuf_from_name(
            "down-icon.svg",
            width=15, height=15
        )
        server_locations_pixbuff = dummy_object.create_icon_pixbuf_from_name(
            "info-circle-filled.svg",
            width=15, height=15
        )
        # Set images and icons
        self.set_icon(window_icon)

        self.headerbar_sign_icon.set_from_pixbuf(protonvpn_headerbar_pixbuf)
        self.overlay_logo_image.set_from_pixbuf(logo_pixbuf)
        self.upload_speed_image.set_from_pixbuf(upload_pixbuff)
        self.download_speed_image.set_from_pixbuf(download_pixbuff)
        self.servers_info_icon.set_from_pixbuf(server_locations_pixbuff)

    def setup_css(self):
        """Setup CSS styles."""
        logger.info("Setting up css")
        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(
            os.path.join(CSS_DIR_PATH, "dashboard.css")
        )
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.set_css_class(self.quick_connect_button, ["primary", "main-button"])
        self.set_css_class(self.main_disconnect_button, ["transparent-danger", "main-button"])
        self.set_css_class(self.cancel_connect_overlay_button, ["transparent-danger", "main-button"])

    def setup_actions(self):
        """Setup actions.

        From documentation:
            Actions represent operations that the user
            can perform, along with some information on
            how it should be presented in the interface.
            Each action provides methods to create icons,
            menu items and toolbar items representing itself.
        (https://developer.gnome.org/gtk3/unstable/GtkAction.html)

        Actions can be mapped to a certain user action (event), instead
        of directly mapping event handlers. Should be used when possible
        to keep UI code portable.
        """
        logger.info("Setting up actions")

        # create action
        cancel_connect_overlay_button = Gio.SimpleAction.new(
            "close_connect_overlay", None
        )
        display_secure_core_popover = Gio.SimpleAction.new(
            "display_secure_core_popover", None
        )
        display_netshield_popover = Gio.SimpleAction.new(
            "display_netshield_popover", None
        )
        display_killswitch_popover = Gio.SimpleAction.new(
            "display_killswitch_popover", None
        )
        quick_connect = Gio.SimpleAction.new(
            "quick_connect", None
        )
        disconnect = Gio.SimpleAction.new(
            "disconnect", None
        )

        # connect action to callback
        cancel_connect_overlay_button.connect(
            "activate", self.on_click_hide_connect_overlay
        )
        display_secure_core_popover.connect(
            "activate",
            self.quick_settings_popover.display_secure_core_settings,
            self.dashboard_secure_core_button_menu
        )
        display_netshield_popover.connect(
            "activate",
            self.quick_settings_popover.display_netshield_settings,
            self.dashboard_netshield_button
        )
        display_killswitch_popover.connect(
            "activate",
            self.quick_settings_popover.display_killswitch_settings,
            self.dashboard_killswitch_button
        )
        quick_connect.connect(
            "activate", self.on_click_quick_connect
        )
        disconnect.connect(
            "activate", self.on_click_disconnect
        )

        # add action
        self.add_action(cancel_connect_overlay_button)
        self.add_action(display_secure_core_popover)
        self.add_action(display_netshield_popover)
        self.add_action(display_killswitch_popover)
        self.add_action(quick_connect)
        self.add_action(disconnect)

        # connect server_search_entry
        self.server_search_entry.connect(
            "search-changed", self.filter_server_list
        )

        # Add tooltip to quick settings buttons
        self.dashboard_secure_core_button_menu.set_property("has-tooltip", True)
        self.dashboard_netshield_button.set_property("has-tooltip", True)
        self.dashboard_killswitch_button.set_property("has-tooltip", True)

        # Set tooltip text
        self.dashboard_secure_core_button_menu.set_tooltip_text("Secure Core")
        self.dashboard_netshield_button.set_tooltip_text("Netshield")
        self.dashboard_killswitch_button.set_tooltip_text("Kill Switch")

        self.connect("delete-event", self.on_close_window)

    def on_close_window(self, dashboard_view, gtk_event, _quit=False):
        if not _quit and self.application.indicator._type != "dummy":
            self.hide()
            return True

        try:
            self.application.indicator.dashboard_action.dispose()
        except AttributeError:
            pass
        self.destroy()

    def filter_server_list(self, server_search_entry):
        """Filter server list based on user input.

        Args:
            server_search_entry: Gtk.SearchEntry
        """
        self.server_list_view.filter_server_list(
            server_search_entry.get_text()
        )

    def gtk_property_setter(self, *args):
        """GTK property setter.

        Args: Following structure:
        {
            "property": "visible",
            "objects": [
                (self.connected_protocol_label, True),
            ]
        }

        Useful to update multiple UI properties in batches.
        Each dict @property value contains the property that
        is desired to change, which then will act on a list of
        @objects. This list contains a tuple, where the first
        argument is the object and the second argument is the value
        that the object property is to be updated to.

        Not useful for only for a couple of UI updates, It is used best
        to update to a certain pre-defined style or state.
        """
        for property_group in args:
            property = property_group.get("property")
            objects = property_group.get("objects")
            for object in objects:
                gtk_object, value = object
                gtk_object.set_property(property, value)

    def add_background_glib(self, glib_source_type: GLibEventSourceEnum):
        """Add background GLib process.

        It initially checks if there is an existent process, so that I does
        not create duplicates (or even more).

        Args:
            glib_source_type (GLibEventSourceEnum)
        """
        if self.glib_source_tracker[
                glib_source_type
        ] is None:
            logger.debug(
                "{} does not exist, adding it.".format(glib_source_type)
            )
            self.glib_source_tracker[
                glib_source_type
            ] = GLib.timeout_add_seconds(
                self.glib_source_updated_time[glib_source_type],
                self.glib_source_updated_method[glib_source_type]
            )

    def remove_background_glib(self, glib_source_type: GLibEventSourceEnum):
        """Remove background GLib process.

        It initially checks there is an existent process, thus avoiding
        any unnenecessary errors/warnings or crashes.

        Args:
            glib_source_type (GLibEventSourceEnum)
        """
        if self.glib_source_tracker[glib_source_type]:
            logger.debug("{} exists, removing source".format(glib_source_type))
            GLib.source_remove(
                self.glib_source_tracker[
                    glib_source_type
                ]
            )
            self.glib_source_tracker[
                glib_source_type
            ] = None

    def prepare_for_app_shutdown(self):
        self.dashboard_view_model.state.dispose()
        self.remove_background_glib(GLibEventSourceEnum.ON_EVENT)
        self.remove_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        self.remove_background_glib(GLibEventSourceEnum.ON_SERVER_LOAD)
        self.remove_background_glib(
            GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED
        )

    def set_css_class(self, gtk_object, add_css_class=None, remove_css_class=None):
        gtk_object_context = gtk_object.get_style_context()

        if isinstance(add_css_class, str):
            if (
                gtk_object_context.has_class(add_css_class)
                or (
                    gtk_object_context.has_class(add_css_class)
                    and remove_css_class
                    and not add_css_class == remove_css_class
                    and not gtk_object_context.has_class(remove_css_class)
                )
            ):
                return

            if remove_css_class:
                if isinstance(remove_css_class, str):
                    if gtk_object_context.has_class(remove_css_class):
                        gtk_object_context.remove_class(remove_css_class)
                else:
                    for css_class in remove_css_class:
                        if gtk_object_context.has_class(css_class):
                            gtk_object_context.remove_class(css_class)

            gtk_object_context.add_class(add_css_class)

        if isinstance(add_css_class, list):
            for css_class in add_css_class:
                self.set_css_class(gtk_object, css_class, remove_css_class)

        if isinstance(remove_css_class, str):
            if gtk_object_context.has_class(remove_css_class):
                gtk_object_context.remove_class(remove_css_class)

        if isinstance(remove_css_class, list):
            for css_class in remove_css_class:
                self.set_css_class(gtk_object, add_css_class, remove_css_class)
