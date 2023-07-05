from ..patterns.factory import BackgroundProcess
from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib import exceptions as lib_exceptions
from protonvpn_nm_lib.enums import ServerTierEnum, SecureCoreStatusEnum
from .dataclass.dashboard import ServerListData, SwitchServerList
from ..logger import logger
from ..module import Module


class ServerListViewModel:
    def __init__(self):
        self.__dashboard_vm = None
        self.__update_server_load = False
        self.server_list_model = Module().server_list_model

    @property
    def dashboard_view_model(self):
        return self.__dashboard_vm

    @dashboard_view_model.setter
    def dashboard_view_model(self, newvalue):
        self.__dashboard_vm = newvalue

    def on_switch_server_list_view_async(self):
        process = BackgroundProcess.factory("gtask")
        process.setup(self.on_switch_server_list_view_sync)
        process.start()

    def on_switch_server_list_view_sync(self, *_):
        state = SwitchServerList(
            display_secure_core=protonvpn.get_settings().secure_core == SecureCoreStatusEnum.ON
        )
        self.__dashboard_vm.state.on_next(state)

    def on_load_servers_async(self, *_):
        process = BackgroundProcess.factory("gtask")
        process.setup(self.on_load_servers)
        process.start()

    def on_load_servers(self, *_):
        self.__generate_server_list()
        state = ServerListData(
            server_list=self.server_list_model,
            display_secure_core=protonvpn.get_settings().secure_core == SecureCoreStatusEnum.ON
        )
        self.__dashboard_vm.state.on_next(state)

    def __generate_server_list(self):
        self.server_list_model.generate_list(
            ServerTierEnum(protonvpn.get_session().vpn_tier)
        )

    def __finish_on_update_server_load(self, self_thread=None, task=None, data=None):
        if self_thread and task:
            var = task.propagate_int()
            if var == 1:
                self.__update_server_load = False
            elif var == 2:
                self.dashboard_view_model.force_logout()

    def on_update_server_load_async(self):
        """Update server Load.

        The main method is started within a background process
        so that the UI will not freeze.

        Since it is being invoked via a GLib method, it returns True
        so that the method can be called again. If returned False,
        then the callback would stop.
        """
        if self.__update_server_load:
            return

        self.__update_server_load = True
        process = BackgroundProcess.factory("gtask")
        process.setup(
            self.__on_update_server_load,
            callback=self.__finish_on_update_server_load
        )
        process.start()

    def __on_update_server_load(self, task=None, self_thread=None, data=None, cancellable=None):
        """Update server load.

        This method refreshes server cache. The library
        will automatically decide what it should cache, so this
        method can be safely used at anytime.

        This method is and should be executed within a python thread.

        The numbers below were defined arbitrarily, meaning that we could easily change then
        to any other values here and inside `__finish_on_update_server_load`, as the meaning
        is only for us, as the Gio.Task doesn't care about the value, as long as it's `int`.
        """
        session = protonvpn.get_session()

        # By requesting the servers, it will automatically trigger a request
        # to the API, to updated the serverlist if needed.
        try:
            _ = session.servers
        except lib_exceptions.APISessionIsNotValidError as e:
            logger.exception(e)
            if task:
                task.return_int(2)
        except Exception as e:
            logger.exception(e)
            if task:
                task.return_int(0)
        else:
            try:
                self.on_load_servers_async(False)
            except Exception as e:
                logger.exception(e)
                if task:
                    task.return_int(0)
            else:
                if task:
                    task.return_int(1)
