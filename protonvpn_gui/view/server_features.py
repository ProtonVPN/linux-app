import os
from abc import abstractmethod
from protonvpn_nm_lib.api import protonvpn
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gdk, Gtk

from ..constants import CSS_DIR_PATH, UI_DIR_PATH
from ..patterns.factory.abstract_widget_factory import WidgetFactory


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "server_features.ui"))
class ServerFeaturesView(Gtk.ApplicationWindow):
    """ServerFeatures view class. GTK Composite object."""
    __gtype_name__ = "ServerFeaturesView"

    server_features_container_grid = Gtk.Template.Child()
    scrolled_window = Gtk.Template.Child()

    def __init__(self, application):
        super().__init__(application=application)
        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(
            os.path.join(CSS_DIR_PATH, "server_features.css")
        )
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.set_position(Gtk.PositionType.BOTTOM)

    def display(self):
        """Display object."""
        self.present()

    @property
    def title(self):
        return self.get_title()

    @title.setter
    def title(self, newvalue):
        return self.set_title(newvalue)

    @abstractmethod
    def __create_widgets():
        """Private method that creates widgets"""
        pass

    @abstractmethod
    def __attach_widgets():
        """Private method that attaches widgets to main container grid"""
        pass


class PremiumCountries():
    def __init__(self, application):
        self.__widget = ServerFeaturesView(application)
        self.__widget.title = "Features"
        self.__widget_list = []
        self.__create_widgets()
        self.__attach_widgets()
        self.__widget.display()

    def __create_widgets(self):
        self.__create_p2p_widget()
        self.__create_streaming_widget()
        self.__create_smart_routing_widget()
        self.__create_tor_widget()

    def __attach_widgets(self):
        counter = 0
        for wiget in self.__widget_list:
            self.__widget.server_features_container_grid.attach(
                wiget.widget, 0, counter, 1, 1
            )
            counter += 1

    def __create_smart_routing_widget(self):
        self.smart_routing = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_smart_routing")
        title = WidgetFactory.label("premium_features_popover_title")
        tier_chip = WidgetFactory.label("premium_features_popover_chip", "PLUS")
        description = WidgetFactory.label("premium_features_popover_description")
        view_more_link = WidgetFactory.button("learn_more")
        view_more_link.add_class("padding-x-none")
        view_more_link.add_class("margin-left-10px")

        title.content = "Smart Routing"
        description.content = "This technology allows ProtonVPN to provide higher" \
            "speed and security in difficult-to-serve countries."
        view_more_link.label = "Learn more"
        view_more_link.url = "https://protonvpn.com/support/smart-routing//"

        self.smart_routing.attach(feature_logo.widget)
        self.smart_routing.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        self.smart_routing.attach_right_next_to(
            tier_chip.widget, title.widget
        )
        self.smart_routing.attach_bottom_next_to(
            description.widget, title.widget, width=2
        )
        self.smart_routing.attach_bottom_next_to(
            view_more_link.widget, description.widget, width=2
        )
        self.__widget_list.append(self.smart_routing)

    def __create_streaming_widget(self):
        self.streaming = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_streaming")
        title = WidgetFactory.label("premium_features_popover_title")
        tier_chip = WidgetFactory.label("premium_features_popover_chip", "PLUS")
        description = WidgetFactory.label("premium_features_popover_description")
        view_more_link = WidgetFactory.button("learn_more")
        view_more_link.add_class("padding-x-none")
        view_more_link.add_class("margin-left-10px")

        title.content = "Streaming"
        description.content = "PLUS server support streaming (Netflix, Disney+, etc) " \
            "from anywhere in the world."
        view_more_link.label = "Learn more"
        view_more_link.url = "https://protonvpn.com/support/streaming-guide/"

        self.streaming.attach(feature_logo.widget,)
        self.streaming.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        self.streaming.attach_right_next_to(
            tier_chip.widget, title.widget
        )
        self.streaming.attach_bottom_next_to(
            description.widget, title.widget, width=2
        )
        self.streaming.attach_bottom_next_to(
            view_more_link.widget, description.widget, width=2
        )
        self.__widget_list.append(self.streaming)

    def __create_p2p_widget(self):
        self.peer2peer = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_p2p")
        title = WidgetFactory.label("premium_features_popover_title")
        tier_chip = WidgetFactory.label("premium_features_popover_chip", "BASIC & PLUS")
        description = WidgetFactory.label("premium_features_popover_description")
        view_more_link = WidgetFactory.button("learn_more")

        title.content = "P2P/BitTorrent"
        description.content = "These servers give the best performance for BitTorrent "\
            "and file sharing."
        view_more_link.label = "Learn more"
        view_more_link.url = "https://protonvpn.com/support/bittorrent-vpn/"
        view_more_link.add_class("padding-x-none")
        view_more_link.add_class("margin-left-10px")

        self.peer2peer.attach(feature_logo.widget)
        self.peer2peer.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        self.peer2peer.attach_right_next_to(
            tier_chip.widget, title.widget
        )
        self.peer2peer.attach_bottom_next_to(
            description.widget, title.widget, width=2
        )
        self.peer2peer.attach_bottom_next_to(
            view_more_link.widget, description.widget, width=2
        )
        self.__widget_list.append(self.peer2peer)

    def __create_tor_widget(self):
        self.tor = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_tor")
        title = WidgetFactory.label("premium_features_popover_title")
        tier_chip = WidgetFactory.label("premium_features_popover_chip", "PLUS")
        description = WidgetFactory.label("premium_features_popover_description")
        view_more_link = WidgetFactory.button("learn_more")

        title.content = "Tor"
        description.content = "Route your Internet traffic through the Tor network. "\
            "Slower but more private."
        view_more_link.label = "Learn more"
        view_more_link.url = "https://protonvpn.com/support/tor-vpn/"
        view_more_link.add_class("padding-x-none")
        view_more_link.add_class("margin-left-10px")

        self.tor.attach(feature_logo.widget)
        self.tor.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        self.tor.attach_right_next_to(
            tier_chip.widget, title.widget
        )
        self.tor.attach_bottom_next_to(
            description.widget, title.widget, width=2
        )
        self.tor.attach_bottom_next_to(
            view_more_link.widget, description.widget, width=2
        )
        self.__widget_list.append(self.tor)


class PlusFeatures:
    def __init__(self, application, country):
        self.__widget = ServerFeaturesView(application)
        self.__widget.title = "Features"
        self.__widget_list = []
        self.__create_widgets(country)
        self.__attach_widgets()
        self.__widget.display()

    def __create_widgets(self, country):
        self.__create_streaming_widget(country)

    def __attach_widgets(self):
        counter = 0
        for wiget in self.__widget_list:
            self.__widget.server_features_container_grid.attach(
                wiget.widget, 0, counter, 1, 1
            )
            counter += 1

    def __create_streaming_widget(self, country):
        self.streaming = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_streaming")
        title = WidgetFactory.label("premium_features_popover_title")
        description = WidgetFactory.label("streaming_description")

        title.content = "Streaming - {}".format(country.country_name)
        description.content = "Connect to a Plus server in this country to start streaming." \
            "\n\nNote: Use a new browser tab and/or clear the cache to ensure new content appears."

        supported_services = self.__add_supported_services(country)
        self.streaming.attach(feature_logo.widget)
        self.streaming.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        self.streaming.attach_bottom_next_to(
            description.widget, title.widget
        )
        self.streaming.attach_bottom_next_to(
            supported_services.widget, description.widget
        )
        description = WidgetFactory.label("streaming_description", "and more")
        self.streaming.attach_bottom_next_to(
            description.widget, supported_services.widget
        )
        self.__widget_list.append(self.streaming)

    def __add_supported_services(self, country):
        streaming_services = protonvpn.get_session().streaming
        streaming_icons = protonvpn.get_session().streaming_icons
        client_config = protonvpn.get_session().clientconfig

        try:
            services = streaming_services[country.entry_country_code]
        except KeyError:
            return

        services.sort(key=lambda service: service["Name"])
        services_grid = WidgetFactory.grid("streaming_icons_container")
        x_pos = 0
        y_pos = 0
        max_items_per_row = 3
        for service in services:
            if client_config.features.streaming_logos and streaming_icons[service.get("Icon")]:
                # dummy_img = WidgetFactory.image("dummy")
                # dummy_img.add_class("margin-y-20px")
                # pixbuf = dummy_img.create_pixbuf_custom_path(
                #     streaming_icons[service.get("Icon")],
                #     width=105, height=105
                # )
                # dummy_img.set_from_pixbuf(pixbuf)
                # dummy_img.show = True
                # service_widget = dummy_img
                service_widget = WidgetFactory.image(
                    "streaming_service_icon", streaming_icons[service.get("Icon")]
                )

            else:
                service_widget = WidgetFactory.label(
                    "streaming_title", service["Name"]
                )

            services_grid.attach(service_widget.widget, x_pos, y_pos)

            if x_pos == max_items_per_row - 1:
                y_pos += 1
                x_pos = 0
            else:
                x_pos += 1

        return services_grid
