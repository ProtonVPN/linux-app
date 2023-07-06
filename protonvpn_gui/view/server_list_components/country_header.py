from .header import Header
from ..server_features import PremiumCountries, ServerFeaturesView
from protonvpn_nm_lib.enums import ServerTierEnum


class CountryHeader:
    """CountryHeader class.

    Creates country headers mainly based on user tier. Has to be instantiated
    before being used.

    Methods:
        - create(current_country, server_list): will automatically figure out
            if the header should be added or not.
    """
    def __init__(self, application):
        self.app = application
        self.__header_tracker = []

    def on_display_premium_features(self, gtk_button):
        """Display features for specific tier"""
        active_windows = self.app.get_windows()
        if not any(type(window) == ServerFeaturesView for window in active_windows):
            PremiumCountries(self.app)

    def create(self, current_country, server_list):
        """Create country header/separator for respective user tier:

        Args:
            server_list: object that can access the amount of servers
                for each tier and the actual user tier.
            current_country: country_item object
        """
        create_header_for_matching_tier = {
            ServerTierEnum.FREE: self.__solve_for_free_user,
            ServerTierEnum.BASIC: self.__solve_for_basic_user,
            ServerTierEnum.PLUS_VISIONARY: self.__solve_for_top_tier,
            ServerTierEnum.PM: self.__solve_for_top_tier,
        }

        try:
            return create_header_for_matching_tier[server_list.user_tier](
                current_country, server_list
            )
        except KeyError:
            return None

    def __solve_for_free_user(self, current_country, server_list):
        if (
            ServerTierEnum.FREE not in self.__header_tracker
            and current_country.minimum_country_tier.value < ServerTierEnum.BASIC.value
        ):
            free_header = self.__setup_free_header(server_list.free_countries_count)
            self.__header_tracker.append(ServerTierEnum.FREE)
            return free_header
        elif (
            ServerTierEnum.BASIC not in self.__header_tracker
            and current_country.minimum_country_tier.value >= ServerTierEnum.BASIC.value
        ):
            basic_and_plus = self.__setup_basic_and_plus_header(
                server_list.basic_countries_count + server_list.plus_countries_count
            )
            self.__header_tracker.append(ServerTierEnum.BASIC)
            return basic_and_plus

        return None

    def __solve_for_basic_user(self, current_country, server_list):
        if (
            ServerTierEnum.BASIC not in self.__header_tracker
            and current_country.minimum_country_tier.value < ServerTierEnum.PLUS_VISIONARY.value
        ):
            basic_header = self.__setup_basic_header(
                server_list.free_countries_count + server_list.basic_countries_count
            )
            self.__header_tracker.append(ServerTierEnum.BASIC)
            return basic_header
        elif (
            ServerTierEnum.PLUS_VISIONARY not in self.__header_tracker
            and current_country.minimum_country_tier.value >= ServerTierEnum.PLUS_VISIONARY.value # noqa
        ):
            plus_header = self.__setup_plus_header(server_list.plus_countries_count)
            self.__header_tracker.append(ServerTierEnum.PLUS_VISIONARY)
            return plus_header

        return None

    def __solve_for_top_tier(self, current_country, server_list):
        if (
            ServerTierEnum.PLUS_VISIONARY not in self.__header_tracker
            and current_country.minimum_country_tier.value <= ServerTierEnum.PLUS_VISIONARY.value # noqa
        ):
            all_locations_header = self.__setup_all_locations_header(
                server_list.total_countries_count
            )
            self.__header_tracker.append(ServerTierEnum.PLUS_VISIONARY)
            return all_locations_header
        elif (
            ServerTierEnum.PM not in self.__header_tracker
            and current_country.minimum_country_tier == ServerTierEnum.PM
        ):
            internal_header = self.__setup_internal_header(
                server_list.internal_countries_count
            )
            self.__header_tracker.append(ServerTierEnum.PM)
            return internal_header

        return None

    def __setup_free_header(self, server_count):
        h = Header(self.app)
        h.title = "FREE Locations ({})".format(server_count)
        h.info_icon_visibility = True
        h.connect_button(self.on_display_premium_features)
        return h

    def __setup_basic_and_plus_header(self, server_count):
        h = Header(self.app)
        h.title = "PLUS Locations ({})".format(server_count)
        h.info_icon_visibility = True
        h.connect_button(self.on_display_premium_features)
        return h

    def __setup_basic_header(self, server_count):
        h = Header(self.app)
        h.title = "BASIC Locations ({})".format(server_count)
        h.info_icon_visibility = True
        h.connect_button(self.on_display_premium_features)
        return h

    def __setup_plus_header(self, server_count):
        h = Header(self.app)
        h.title = "PLUS Locations ({})".format(server_count)
        h.info_icon_visibility = True
        h.connect_button(self.on_display_premium_features)
        return h

    def __setup_internal_header(self, server_count):
        h = Header(self.app)
        h.title = "Internal ({})".format(server_count)
        return h

    def __setup_all_locations_header(self, server_count):
        h = Header(self.app)
        h.title = "Locations ({})".format(server_count)
        h.info_icon_visibility = True
        h.connect_button(self.on_display_premium_features)
        return h
