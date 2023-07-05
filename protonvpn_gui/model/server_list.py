from protonvpn_nm_lib.api import protonvpn

from ..module import Module
import concurrent.futures


class ServerList:
    """DashboardServerList class.

    This class holds the list of servers that are to be fed to the
    dashboardserver list. This class can either generate a list with
    secure core servers or a list with non-secure servers.

    Properties:
        server_list: list
            contains a list of CountryItem

    Methods:
        generate_list()
            generates the necessary elements for server listing and
            stores them in server_list
    """
    def __init__(self):
        self.__none_secure_core_servers = Module().non_secure_core_servers_model
        self.__secure_core_servers = Module().secure_core_servers_model

    @property
    def none_secure_core(self):
        return self.__none_secure_core_servers

    @property
    def secure_core(self):
        return self.__secure_core_servers

    def generate_list(self, user_tier):
        """Generate server list.

        Args:
            user_tier (ServerTierEnum)
        """
        unfiltered_server_list = []
        server_list = protonvpn.get_session().servers
        server_filter = protonvpn.get_session().servers.filter
        country_code_with_matching_servers = self\
            .__get_country_code_with_matching_servers(server_list)

        self.__none_secure_core_servers.user_tier = user_tier
        self.__secure_core_servers.user_tier = user_tier

        for country_code, servername_list in country_code_with_matching_servers.items(): # noqa
            country_item = Module().country_item_model()
            country_item.create(
                servername_list, server_filter,
                user_tier, country_code
            )

            unfiltered_server_list.append(country_item)

        _jobs = [
            [self.__secure_core_servers, unfiltered_server_list],
            [self.__none_secure_core_servers, unfiltered_server_list],
        ]

        with concurrent.futures.ProcessPoolExecutor() as exec:
            res = exec.map(self._generate_process, _jobs)
            for instance, servers in list(res):
                if isinstance(instance, type(self.__secure_core_servers)):
                    self.__secure_core_servers.servers = servers
                elif isinstance(instance, type(self.__none_secure_core_servers)):
                    self.__none_secure_core_servers.servers = servers

    def _generate_process(self, data):
        instance = data[0]
        servers = data[1]

        return instance, instance.generate(servers)

    def __get_country_code_with_matching_servers(self, server_list):
        country = protonvpn.get_country()
        return country\
            .get_dict_with_country_code_servername(
                server_list
            )
