import gi
from protonvpn_nm_lib.enums import FeatureEnum, ServerStatusEnum

from ...enums import GLibEventSourceEnum
from ...patterns.factory import WidgetFactory
from ..dialog import ConnectUpgradeDialog
from .server_load import ServerLoad

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from ..server_features import CountryStreamingWidget


class ServerRow:
    def __init__(self, dasbhoard_view, country, server, display_sc):
        self.dv = dasbhoard_view
        self.grid = WidgetFactory.grid("server_row")
        self.grid.add_class("server-row")
        self.left_child = ServerRowLeftGrid(self.dv, country, server, display_sc)
        self.right_child = ServerRowRightGrid(self.dv, server)
        self.grid.attach(self.left_child.grid.widget)
        self.grid.attach_right_next_to(
            self.right_child.grid.widget,
            self.left_child.grid.widget,
        )
        self.create_event_box(server)

    def create_event_box(self, server):
        self.event_box = Gtk.EventBox()
        self.event_box.set_visible_window(True)
        self.event_box.add(self.grid.widget)
        self.event_box.props.visible = True

        if server.status == ServerStatusEnum.UNDER_MAINTENANCE:
            return

        self.event_box.connect(
            "enter-notify-event", self.right_child.on_server_enter
        )
        self.event_box.connect(
            "leave-notify-event", self.right_child.on_server_leave
        )


class ServerRowLeftGrid:
    def __init__(self, dv, country, server, display_sc):
        self.dv = dv
        self.server = server
        self.country = country
        self.feature_icon_list = []
        self.display_sc = display_sc
        self.grid = WidgetFactory.grid("left_child_in_server_row")
        self.populate_left_grid()

        if not server.status.value:
            self.servername_label.add_class("disabled-label")

    def populate_left_grid(self):
        self.create_load_icon()
        self.create_exit_flag()
        self.create_servername_label()
        self.create_secure_core_chevron()
        if not self.display_sc:
            self.set_server_features()

    def create_load_icon(self):
        self.load_icon = ServerLoad(self.server.load)
        self.load_icon.show_all()
        self.grid.attach(self.load_icon)

    def create_exit_flag(self):
        try:
            self.country_flag = WidgetFactory.image(
                "small_flag", self.server.entry_country_code
            )
            self.country_flag.remove_class("country-flag")
            self.country_flag.add_class("margin-left-10px")
            self.country_flag.add_class("margin-right-10px")
        except gi.repository.GLib.Error:
            self.country_flag = WidgetFactory.image("dummy_small_flag")

        self.grid.attach_right_next_to(
            self.country_flag.widget,
            self.load_icon,
        )

        self.country_flag.show = True if self.display_sc else False

    def create_servername_label(self):
        self.servername_label = WidgetFactory.label(
            "server", self.server.name
        )
        if self.display_sc:
            from protonvpn_nm_lib.country_codes import country_codes

            country_name = country_codes.get(
                self.server.entry_country_code,
                self.server.entry_country_code
            )
            self.servername_label.content = "via {}".format(country_name)

        self.grid.attach_right_next_to(
            self.servername_label.widget,
            self.country_flag.widget,
        )

    def create_secure_core_chevron(self):
        self.sc_chevron = WidgetFactory.image("secure_core_chevron")
        self.grid.attach_right_next_to(
            self.sc_chevron.widget,
            self.servername_label.widget,
        )
        self.sc_chevron.show = True if self.display_sc else False

    def set_server_features(self):
        feature_to_img_dict = {
            FeatureEnum.TOR: ["tor_icon", "Tor Server"],
            FeatureEnum.P2P: ["p2p_icon", "P2P Server"],
            FeatureEnum.STREAMING: ["streaming_icon", "Streaming"],
        }

        features = self.server.features
        if len(features) < 1 or len(features) == 1 and (
            FeatureEnum.NORMAL not in features
            or FeatureEnum.SECURE_CORE not in features
        ):
            return

        for feature in features:
            try:
                pixbuf_feature_icon = WidgetFactory.image(
                    feature_to_img_dict[feature][0]
                )
            except KeyError:
                continue
            pixbuf_feature_icon.tooltip = True
            pixbuf_feature_icon.tooltip_text = feature_to_img_dict[feature][1]

            if feature == FeatureEnum.STREAMING:
                _button = WidgetFactory.button("server_row_streaming_feature")
                _w = CountryStreamingWidget(self.dv.application, self.country)
                _button.custom_content(pixbuf_feature_icon.widget)
                _button.connect(
                    "clicked", _w.display
                )
                pixbuf_feature_icon = _button

            self.attach_feature_icon(pixbuf_feature_icon.widget)

    def attach_feature_icon(self, pixbuf_feature_icon):
        if len(self.feature_icon_list) < 1:
            self.grid.attach_right_next_to(
                pixbuf_feature_icon,
                self.servername_label.widget
            )
        else:
            gtk_image = self.feature_icon_list[-1]
            self.grid.attach_right_next_to(pixbuf_feature_icon, gtk_image)

        self.feature_icon_list.append(pixbuf_feature_icon)


class ServerRowRightGrid:
    def __init__(self, dasbhoard_view, server):
        self.dv = dasbhoard_view
        self.grid = WidgetFactory.grid("right_child_in_server_row")
        self.maintenance_icon = WidgetFactory.image("maintenance_icon")
        self.connect_server_button = WidgetFactory.button("connect_server")
        self.city_label = WidgetFactory.label("city", server.city)
        self.maintenance_icon.tooltip = True
        self.maintenance_icon.tooltip_text = "Under maintenance"
        server_under_maintenance = server.status == ServerStatusEnum.UNDER_MAINTENANCE

        self.maintenance_icon.show = server_under_maintenance
        self.city_label.show = not server_under_maintenance
        object_to_attach = (
            self.maintenance_icon
            if server_under_maintenance
            else self.connect_server_button
        )

        # Both widgets are attached to the same position
        # as they are mutually exclusive. Only one at the
        # time can be displayed.
        self.grid.attach(self.city_label.widget)
        self.grid.attach(object_to_attach.widget)

        if server_under_maintenance:
            return

        self.connect_server_button.connect(
            "clicked", self.connect_to_server,
            server.name, server.has_to_upgrade
        )

        if server.has_to_upgrade:
            self.connect_server_button.label = "UPGRADE"
            self.city_label.content = "Upgrade"

    def connect_to_server(self, gtk_button_object, servername, user_has_to_upgrade):
        if user_has_to_upgrade:
            ConnectUpgradeDialog(self.dv.application)
        else:
            self.dv.remove_background_glib(
                GLibEventSourceEnum.ON_MONITOR_VPN
            )
            self.dv.dashboard_view_model.on_servername_connect(servername)

    def on_server_enter(self, gtk_widget, event_crossing):
        """Show connect button on enter country row."""
        self.city_label.show = False
        self.connect_server_button.show = True

    def on_server_leave(self, gtk_widget, event_crossing):
        """Hide connect button on leave country row."""
        if event_crossing.detail in [
            Gdk.NotifyType.NONLINEAR,
            Gdk.NotifyType.NONLINEAR_VIRTUAL,
            Gdk.NotifyType.ANCESTOR,
            Gdk.NotifyType.VIRTUAL
        ]:
            self.connect_server_button.show = False
            self.city_label.show = True
