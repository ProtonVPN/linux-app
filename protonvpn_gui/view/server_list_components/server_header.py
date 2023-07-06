from protonvpn_nm_lib.enums import ServerTierEnum
from .header import Header
from ..server_features import PlusFeatures, ServerFeaturesView
from protonvpn_nm_lib.api import protonvpn


class ServerHeader:
    """ServerHeader class."""
    def __init__(self, application):
        self.app = application
        self.__header_tracker = []

    def create(self, current_server, country_item):
        """Create country header/separator for respective user tier:

        Args:
            server_list: object that can access the amount of servers
                for each tier and the actual user tier.
            current_server: country_item object
        """
        if (
            current_server.tier == ServerTierEnum.FREE
            and ServerTierEnum.FREE not in self.__header_tracker
        ):
            h = Header(self.app)
            h.title = "FREE Servers ({})".format(country_item.ammount_of_free_servers)
            self.__header_tracker.append(ServerTierEnum.FREE)
            return h
        elif (
            current_server.tier == ServerTierEnum.BASIC
            and ServerTierEnum.BASIC not in self.__header_tracker
        ):
            h = Header(self.app)
            h.title = "BASIC Servers ({})".format(country_item.ammount_of_basic_servers)
            self.__header_tracker.append(ServerTierEnum.BASIC)
            return h
        elif (
            current_server.tier == ServerTierEnum.PLUS_VISIONARY
            and ServerTierEnum.PLUS_VISIONARY not in self.__header_tracker
        ):
            h = Header(self.app)
            h.title = "PLUS Servers ({})".format(country_item.ammount_of_plus_servers)
            self.__header_tracker.append(ServerTierEnum.PLUS_VISIONARY)
            try:
                protonvpn.get_session().streaming[country_item.entry_country_code]
                h.info_icon_visibility = True
                h.connect_button(self.on_display_plus_features, country_item)
            except KeyError:
                pass

            return h
        elif (
            current_server.tier == ServerTierEnum.PM
            and ServerTierEnum.PM not in self.__header_tracker
        ):
            h = Header(self.app)
            h.title = "Internal Servers ({})".format(country_item.ammount_of_internal_servers)
            self.__header_tracker.append(ServerTierEnum.PM)
            return h

        return None

    def on_display_plus_features(self, gtk_button, country_item=None):
        """Display features for specific tier"""
        active_windows = self.app.get_windows()
        if not any(type(window) == ServerFeaturesView for window in active_windows):
            if not country_item:
                return

            PlusFeatures(self.app, country_item)
