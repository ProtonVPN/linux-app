from protonvpn_nm_lib.enums import ServerStatusEnum, ServerTierEnum, FeatureEnum
from protonvpn_nm_lib.country_codes import country_codes
from ..module import Module
from abc import abstractmethod, ABCMeta
from ..utils import SubclassesMixin


class CountryItemFactory(SubclassesMixin, metaclass=ABCMeta):

    @classmethod
    def factory(cls, type="default"):
        subclasses_dict = cls._get_subclasses_dict("country_item")
        return subclasses_dict[type]

    @property
    @abstractmethod
    def country_name():
        raise NotImplementedError()

    @country_name.setter
    @abstractmethod
    def country_name():
        raise NotImplementedError()

    @property
    @abstractmethod
    def entry_country_code():
        raise NotImplementedError()

    @entry_country_code.setter
    @abstractmethod
    def entry_country_code():
        raise NotImplementedError()

    @property
    @abstractmethod
    def status():
        raise NotImplementedError()

    @property
    @abstractmethod
    def tiers():
        raise NotImplementedError()

    @property
    @abstractmethod
    def features():
        raise NotImplementedError()

    @property
    @abstractmethod
    def servers():
        raise NotImplementedError()

    @servers.setter
    @abstractmethod
    def servers():
        raise NotImplementedError()

    @property
    @abstractmethod
    def can_connect():
        raise NotImplementedError()

    @property
    @abstractmethod
    def minimum_country_tier():
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_virtual():
        raise NotImplementedError()

    @property
    @abstractmethod
    def ammount_of_free_servers():
        raise NotImplementedError()

    @property
    @abstractmethod
    def ammount_of_basic_servers():
        raise NotImplementedError()

    @property
    @abstractmethod
    def ammount_of_plus_servers():
        raise NotImplementedError()

    @property
    @abstractmethod
    def ammount_of_internal_servers():
        raise NotImplementedError()

    @property
    @abstractmethod
    def create():
        raise NotImplementedError()


class CountryItem(CountryItemFactory):
    """CountryItem class.

    Represents a country item in the list of servers. This object stores
    information about a country and also a list of servers that it provides.

    Properties:
        country_name : str
            country name that is set by the view
        entry_country_code: str
            ISO country code
        status: ServerStatusEnum
            country server status
        tiers: list
            the tiers that this country has
        features: list
            features that this country provides
        servers: list
            contains a list of ServerItem

    All the properties can be reached from the outside, but only two can be
    set outside of it's own class, entry_country_code and country_name.

    entry_country_code: this is set in the class that builds this object,
    thus avoiding to pass any the country code as an argument.

    country_name: since country names are dependent on
    their translation (view level) so it does not make sense to hard-code
    it here. Also, this property, after being set, shall be used to
    sort countries in alphabetical order.
    """
    country_item = "default"

    def __init__(self):
        self.__entry_country_code: str = None
        self.__status: ServerStatusEnum = None
        self.__tiers: list = []
        self.__features: list = set()
        self.__servers: list = []
        self.__can_connect: bool = False
        self.__minimum_required_tier = None
        self.__is_virtual_country: bool = None
        self.__country_name: str = None

    @staticmethod
    def init():
        return CountryItem()

    def __len__(self):
        return len(self.__servers)

    @property
    def server_filter(self):
        return

    @property
    def country_name(self):
        return self.__country_name

    @country_name.setter
    def country_name(self, new_country_name):
        self.__country_name = new_country_name

    @property
    def entry_country_code(self):
        return self.__entry_country_code

    @entry_country_code.setter
    def entry_country_code(self, new_entry_country_code):
        self.__entry_country_code = new_entry_country_code

    @property
    def status(self):
        return self.__status

    @property
    def tiers(self):
        return self.__tiers

    @property
    def features(self):
        return self.__features

    @property
    def servers(self):
        return self.__servers

    @servers.setter
    def servers(self, newvalue):
        self.__servers = newvalue

    @property
    def can_connect(self):
        return self.__can_connect

    @property
    def minimum_country_tier(self):
        return self.__minimum_required_tier

    @property
    def is_virtual(self):
        return self.__is_virtual_country

    @property
    def ammount_of_free_servers(self):
        num_free_countries = 0
        for server in self.servers:
            if server.tier == ServerTierEnum.FREE:
                num_free_countries += 1

        return num_free_countries

    @property
    def ammount_of_basic_servers(self):
        num_basic_countries = 0
        for server in self.servers:
            if server.tier == ServerTierEnum.BASIC:
                num_basic_countries += 1

        return num_basic_countries

    @property
    def ammount_of_plus_servers(self):
        num_plus_countries = 0
        for server in self.servers:
            if server.tier == ServerTierEnum.PLUS_VISIONARY:
                num_plus_countries += 1

        return num_plus_countries

    @property
    def ammount_of_internal_servers(self):
        num_internal_countries = 0
        for server in self.servers:
            if server.tier.value >= ServerTierEnum.PM.value:
                num_internal_countries += 1

        return num_internal_countries

    def create(
        self, servername_list,
        server_filter, user_tier, country_code
    ):
        status_collection = set()
        tier_collection = set()
        feature_collection = set()
        country_host_collection = []
        self.__entry_country_code = country_code

        for servername in servername_list:
            logical_server = server_filter(
                lambda server: server.name.lower() == servername.lower()
            )[0]
            server_item = Module().server_item_model()

            server_item.create(logical_server, user_tier)

            self.__servers.append(server_item)
            self.__add_feature_to_collection(
                feature_collection, server_item.features
            )
            self.__add_status_to_collection(
                status_collection, server_item.status
            )
            self.__add_tier_to_collection(tier_collection, server_item.tier)
            if FeatureEnum.SECURE_CORE not in logical_server.features:
                country_host_collection.append(logical_server.host_country)

        self.__set_features(feature_collection)
        self.__set_status(status_collection)
        self.__set_tiers(tier_collection)
        self.__set_minimum_required_tier(tier_collection)
        self.__country_name = country_codes.get(
            self.__entry_country_code,
            self.__entry_country_code
        )
        self.__can_connect = True\
            if (
                (
                    user_tier == ServerTierEnum.FREE
                    and ServerTierEnum.FREE in self.__tiers
                ) or (
                    user_tier.value > ServerTierEnum.FREE.value
                )

            ) else False
        self.__is_virtual_country = all(country_host_collection)

    def __add_feature_to_collection(
        self, feature_collection, server_features
    ):
        for feature in server_features:
            feature_collection.add(feature)

    def __add_status_to_collection(self, status_collection, server_status):
        status_collection.add(server_status)

    def __add_tier_to_collection(self, tier_collection, server_tier):
        tier_collection.add(server_tier)

    def __set_features(self, features_collector):
        self.__features = list(features_collector)

    def __set_status(self, status_collection):
        self.__status = self.__get_country_status(list(status_collection))

    def __set_tiers(self, tier_collection):
        self.__tiers = list(tier_collection)

    def __set_minimum_required_tier(self, tier_collection):
        for tier in tier_collection:
            if not self.__minimum_required_tier:
                self.__minimum_required_tier = tier
                continue
            elif self.__minimum_required_tier.value > tier.value:
                self.__minimum_required_tier = tier

    def __get_country_status(self, status_collection):
        if ServerStatusEnum.ACTIVE in status_collection:
            return ServerStatusEnum.ACTIVE
        else:
            return ServerStatusEnum.UNDER_MAINTENANCE
