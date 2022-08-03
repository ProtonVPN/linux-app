from protonvpn_nm_lib import exceptions
from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.enums import (ConnectionMetadataEnum,
                                    ConnectionStartStatusEnum,
                                    ConnectionStatusEnum, ConnectionTypeEnum,
                                    FeatureEnum, KillswitchStatusEnum,
                                    NetshieldTranslationEnum, NotificationEnum,
                                    NotificationStatusEnum,
                                    SecureCoreStatusEnum,
                                    VPNConnectionReasonEnum,
                                    VPNConnectionStateEnum)

from ..enums import (DashboardKillSwitchIconEnum, DashboardNetshieldIconEnum,
                     DashboardSecureCoreIconEnum)
from ..logger import logger
from ..module import Module
from ..patterns.factory import BackgroundProcess
from ..rx.subject.replaysubject import ReplaySubject
from .dataclass import dashboard as dt


class DashboardViewModel:
    """Dashboard View Model.

    Uses the protonvpn library to take different actions.
    It uses the state variable to notify the View (which is
    listening and awaiting for any changes), to update the UI
    accordingly.

    Due to the fact that the protonvpn library uses GLib (which
    the UI is also running on) to add, start, remove and stop
    connections it is currently no possible to execute these
    in a thread/background to make the UI more fluid. Thus, the main thread
    is passed back and forth (from library to UI and vice-versa)
    to execute these processes. Thus, whenever possible, python threads
    are used so that the UI changes are more fluid.

    All threads should run in daemon mode, so that when the program is closed,
    all threads are also closed.
    """

    _conn_state_msg = {
        VPNConnectionStateEnum.UNKNOWN: "State of "
        "VPN connection is unkown.",
        VPNConnectionStateEnum.NEEDS_CREDENTIALS: "The VPN "
        "connection is missing credentials.",
        VPNConnectionStateEnum.FAILED: "Failed to "
        "connect to VPN.",
        VPNConnectionStateEnum.DISCONNECTED: "VPN connection "
        "has been disconnected.",
        VPNConnectionStateEnum.UNKNOWN_ERROR: "Unknown error."
    }

    _conn_reason_msg = {
        VPNConnectionReasonEnum.UNKNOWN: "The reason for the active "
        "connection state change is unknown.",
        VPNConnectionReasonEnum.NOT_PROVIDED: "No reason was given "
        "for the active connection state change.",
        VPNConnectionReasonEnum.USER_HAS_DISCONNECTED: "The active "
        "connection changed state because the user "
        "disconnected it.",
        VPNConnectionReasonEnum.DEVICE_WAS_DISCONNECTED: "The active "
        "connection changed state because the device it was using "
        "was disconnected.",
        VPNConnectionReasonEnum.SERVICE_PROVIDER_WAS_STOPPED: "The "
        "service providing the VPN connection was stopped.",
        VPNConnectionReasonEnum.IP_CONFIG_WAS_INVALID: "The IP "
        "configuration of the active connection is invalid.",
        VPNConnectionReasonEnum.CONN_ATTEMPT_TO_SERVICE_TIMED_OUT: "The "
        "connection attempt to the VPN service timed out.",
        VPNConnectionReasonEnum.TIMEOUT_WHILE_STARTING_VPN_SERVICE_PROVIDER: # noqa
        "A timeout occurred while starting the service providing "
        "the VPN connection.",
        VPNConnectionReasonEnum.START_SERVICE_VPN_CONN_SERVICE_FAILED:
        "Starting the service providing the VPN connection failed.",
        VPNConnectionReasonEnum.SECRETS_WERE_NOT_PROVIDED: "Necessary "
        "secrets for the connection were not provided.",
        VPNConnectionReasonEnum.SERVER_AUTH_FAILED: "Authentication "
        "to the server failed.",
        VPNConnectionReasonEnum.DELETED_FROM_SETTINGS: "The connection "
        "was deleted from settings.",
        VPNConnectionReasonEnum.MASTER_CONN_FAILED_TO_ACTIVATE: "Master "
        "connection failed to activate.",
        VPNConnectionReasonEnum.CREATE_SOFTWARE_DEVICE_LINK_FAILED:
        "Could not create the software device link.",
        VPNConnectionReasonEnum.VPN_DEVICE_DISAPPEARED: "The device this "
        "connection depended on disappeared.",
        VPNConnectionReasonEnum.UNKNOWN_ERROR: "Unknown reason occured."
    }

    ks_quick_setting = {
        KillswitchStatusEnum.DISABLED: DashboardKillSwitchIconEnum.OFF,
        KillswitchStatusEnum.SOFT: DashboardKillSwitchIconEnum.ON_ACTIVE,
        KillswitchStatusEnum.HARD:
        DashboardKillSwitchIconEnum.ALWAYS_ON_ACTIVE
    }
    ns_quick_setting = {
        NetshieldTranslationEnum.DISABLED: DashboardNetshieldIconEnum.OFF,
        NetshieldTranslationEnum.MALWARE:
        DashboardNetshieldIconEnum.MALWARE_ACTIVE,
        NetshieldTranslationEnum.ADS_MALWARE:
        DashboardNetshieldIconEnum.MALWARE_ADS_ACTIVE
    }
    sc_quick_setting = {
        SecureCoreStatusEnum.OFF: DashboardSecureCoreIconEnum.OFF,
        SecureCoreStatusEnum.ON: DashboardSecureCoreIconEnum.ON_ACTIVE
    }

    def __init__(self):
        self.utils = Module().utility
        self.__none_vpn_ip = None
        self.__none_vpn_isp = None
        self.__none_vpn_contry_code = None
        self.__quick_settings_vm = Module().quick_settings_view_model
        self.__server_list_vm = Module().server_list_view_model

        self.__quick_settings_vm.dashboard_view_model = self
        self.__server_list_vm.dashboard_view_model = self

        self.__state = ReplaySubject(buffer_size=1)

    @property
    def state(self):
        from protonvpn_gui.rx.internal.exceptions import DisposedException
        try:
            self.__state.check_disposed()
        except DisposedException:
            self.__state = ReplaySubject(buffer_size=1)

        return self.__state

    @state.deleter
    def state(self):
        self.__state.dispose()

    @property
    def quick_settings_view_model(self):
        return self.__quick_settings_vm

    @property
    def server_list_view_model(self):
        return self.__server_list_vm

    def on_switch_secure_core_button(self, *args):
        self.__quick_settings_vm.on_switch_secure_core_button(*args)

    def on_switch_netshield_button(self, *args):
        self.__quick_settings_vm.on_switch_netshield_button(*args)

    def on_switch_killswitch_button(self, *args):
        self.__quick_settings_vm.on_switch_killswitch_button(*args)

    def on_update_server_load(self):
        self.__server_list_vm.on_update_server_load_async()
        return True

    def on_startup_preload_resources_async(self):
        """Async load initial UI components such as quick settings and
        server list."""
        process = BackgroundProcess.factory("gtask")
        process.setup(self.__on_startup)
        process.start()

    def __on_startup(self, *_):
        """Load initial UI components such as quick settings and
        server list.

        This needs to be pre-loaded before displaying the dashboard."""
        self.__display_new_brand_dialog_if_not_opened()
        self.check_if_events_should_be_displayed()
        self.state.on_next(self.get_quick_settings_state())

        try:
            self.__server_list_vm.on_load_servers()
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            result = dt.DisplayDialog(
                title="Error Loading Servers",
                text=str(e)
            )
            self.state.on_next(result)

    def async_check_if_events_should_be_displayed(self):
        """Async check if events should be displayed."""
        process = BackgroundProcess.factory("gtask")
        process.setup(self.check_if_events_should_be_displayed)
        process.start()

        return True

    def __display_new_brand_dialog_if_not_opened(self):
        print("Running display new brand dialog")
        print("protonvpn.get_settings().new_brand", protonvpn.get_settings().new_brand)
        if protonvpn.get_settings().new_brand == NotificationStatusEnum.NOT_OPENED:
            self.state.on_next(
                dt.DisplayEvent(
                    dt.WelcomeToNewBrandEvent(None), False, self.set_new_brand_dialog_opened
                )
            )

    def check_if_events_should_be_displayed(self, *_):
        """Sync check if events should be displayed."""
        all_notitications = protonvpn.get_session().get_all_notifications()
        if not isinstance(all_notitications, list):
            return

        for event in all_notitications:
            # Check if the notifications is of generic event type
            # also check if it can be displayed,
            # If both are false then nothing will be displayed
            if event.notification_type == NotificationEnum.GENERIC.value:
                self.state.on_next(
                    dt.DisplayEvent(
                        dt.GenericEvent(event),
                        (
                            True
                            if protonvpn.get_settings().event_notification == NotificationStatusEnum.OPENED # noqa
                            else False
                        ),
                        self.set_notification_as_read
                    )
                )

    def set_notification_as_read(self):
        protonvpn.get_settings().event_notification = NotificationStatusEnum.OPENED

    def set_new_brand_dialog_opened(self):
        protonvpn.get_settings().new_brand = NotificationStatusEnum.OPENED

    def on_startup_load_dashboard_resources_async(self, *_):
        """Async load dashboard resources."""
        process = BackgroundProcess.factory("gtask")
        process.setup(self.__on_startup_load_dashboard_resources)
        process.start()

    def __on_startup_load_dashboard_resources(self, *_):
        """Load dashboard resources.

        This updates the rest of dashboard UI components.
        """
        try:
            protonvpn.ensure_connectivity()
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            result = dt.NotConnectedToVPNInfo(
                ip=None,
                isp=None,
                country=None,
                perma_ks_enabled=protonvpn.get_settings().killswitch == KillswitchStatusEnum.HARD
            )
        else:
            try:
                if not protonvpn.get_active_protonvpn_connection():
                    result = self._get_not_connected_state()
                else:
                    result = self._get_connected_state()
            except (exceptions.ProtonVPNException, Exception) as e:
                logger.exception(e)
                result = dt.DisplayDialog(
                    title="Error Getting VPN State",
                    text=str(e)
                )

        self.state.on_next(result)

    def on_quick_connect(self):
        """Quick connect to Proton VPN.

        This method sets the state of the UIsync_async
        to preparing and calls the method
        connect() with ConnectionTypeEnum type.

        Ideally the on_quick_connect() method should be run
        within a python thread. Due to current situation, it is
        not done so due the reasons specified in class docstring.
        """
        logger.info("Preparing to quick connect")
        self.connect(ConnectionTypeEnum.FASTEST)

    def on_country_connect(self, country_code):
        """Connect to a specific country.

        This method sets the state of the UI
        to preparing and calls the method
        connect() with ConnectionTypeEnum type.

        Ideally this method should be run
        as a background process.
        """
        logger.info("Preparing to connect to country \"{}\"".format(
            country_code
        ))
        self.connect(
            ConnectionTypeEnum.COUNTRY,
            country_code
        )

    def on_servername_connect(self, servername):
        """Connect to a specific server.

        This method sets the state of the UI
        to preparing and calls the method
        connect() with ConnectionTypeEnum type.

        Ideally this method should be run
        as a background process.
        """
        logger.info("Preparing to connect to servername \"{}\"".format(
            servername
        ))
        self.connect(
            ConnectionTypeEnum.SERVERNAME,
            servername
        )

    def on_reconnect(self):
        """Reconnect to previously connected server.

        This method sets the state of the UI
        to preparing and calls the method
        connect() with ConnectionTypeEnum type.

        Ideally this method should be run
        as a background process.
        """
        logger.info("Preparing to reconnect")
        self.connect(connection_type_enum=None, reconnect=True)

    def connect(self, connection_type_enum, extra_arg=None, reconnect=False):
        """General connect method.

        This method should always be used when connecting to
        VPN. Ideally should be run within a python thread.

        It initially attemps to setup the connection, then updated
        the UI accordingly and only the proceeds to connect to the VPN.
        This is done so that the user is aware of where the connections
        is made to during the ConnectInProgressInfo() state.

        Args:
            connection_type_enum (ConnectionTypeEnum)
            extra_arg: (optional)
                this argument is only set if the user is
                connecting with ConnectionTypeEnum.COUNTRY
                or ConnectionTypeEnum.SERVERNAME.
        """
        logger.info("Setting up connection")
        self.state.on_next(dt.ConnectPreparingInfo())

        setup_connection_error = False
        display_troubleshoot_dialog = False
        try:
            if reconnect:
                server = protonvpn.setup_reconnect()
            else:
                server = protonvpn.setup_connection(
                    connection_type=connection_type_enum,
                    connection_type_extra_arg=extra_arg
                )
        except exceptions.ServerCacheNotFound as e:
            logger.exception(e)
            setup_connection_error = \
                "\nServer cache is missing. " \
                "Please ensure that you have internet connection to " \
                "cache servers."
            display_troubleshoot_dialog = True
        except exceptions.ServernameServerNotFound as e:
            logger.exception(e)
            setup_connection_error = \
                "\nNo server could be found with the provided servername.\n" \
                "Possibly the server went under maintenance"
        except exceptions.DefaultOVPNPortsNotFoundError as e:
            logger.exception(e)
            setup_connection_error = \
                "\nThere are missing configurations. " \
                "Please ensure that you have internet connection."
            display_troubleshoot_dialog = True
        except exceptions.DisableConnectivityCheckError as e:
            logger.exception(e)
            setup_connection_error = \
                "\nIt was not possible to automatically disable connectivity check. " \
                "This step is necessary for the Kill Switch to function properly, " \
                "please disable connectivity check copying and pasting the following" \
                "command into terminal:\nbusctl set-property org.freedesktop.NetworkManager " \
                "/org/freedesktop/NetworkManager org.freedesktop.NetworkManager " \
                "ConnectivityCheckEnabled 'b' 0"
        except exceptions.InsecureConnection as e:
            logger.exception(e)
            setup_connection_error = "Your connection is not secure. " \
                "Please change network and attempt a new connection.",
            display_troubleshoot_dialog = True
        except exceptions.APITimeoutError as e:
            logger.exception(e)
            setup_connection_error = "Connection to API timed out."
            display_troubleshoot_dialog = True
        except exceptions.APIError as e:
            logger.exception(e)
            setup_connection_error = "Error in reaching API."
            display_troubleshoot_dialog = True
        except exceptions.NetworkConnectionError as e:
            logger.exception(e)
            setup_connection_error = "Network Error"
            display_troubleshoot_dialog = True
        except exceptions.UnreacheableAPIError as e:
            logger.exception(e)
            setup_connection_error = "Unable to reach API"
            display_troubleshoot_dialog = True
        except exceptions.UnknownAPIError as e:
            logger.exception(e)
            setup_connection_error = "Unknown API error.",
            display_troubleshoot_dialog = True
        except (
            exceptions.API8002Error, exceptions.API5002Error,
            exceptions.API5003Error, exceptions.API85031Error,
            exceptions.API12087Error, exceptions.API2011Error
        ) as e:
            logger.exception(e)
            setup_connection_error = str(e)
            display_troubleshoot_dialog = True
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            setup_connection_error = \
                "\nAn unknown error has occured. Please ensure that you have " \
                "internet connectivity." \
                "\nIf the issue persists, please contact support."
            display_troubleshoot_dialog = True

        if setup_connection_error:
            result = dt.ConnectError(
                setup_connection_error,
                display_troubleshoot_dialog
            )
            self.state.on_next(result)
            return

        logger.info("Connection was setup")
        # step 1
        self.__display_connection_information_during_connect(server)

        # step 2
        logger.info("Attempting to connect")
        reason_message = "Error -999"
        state = None

        try:
            connect_response = protonvpn.connect()
        except exceptions.AccountIsDelinquentError as e:
            logger.exception(e)
            self.__quick_settings_vm.on_switch_secure_core_button(SecureCoreStatusEnum.OFF, True)
            self.__quick_settings_vm.on_switch_netshield_button(NetshieldTranslationEnum.DISABLED, True)
            result = dt.DisplayDialog(
                title="Deliquent Account",
                text="The account is flagged as delinquent due to unpaid invoices. "
                "You can continue to use Proton VPN, but any paid features are now disabled."
            )
            self.state.on_next(result)
            self.connect(ConnectionTypeEnum.FREE)
            self.__server_list_vm.on_load_servers()
            return
        except exceptions.AccountWasDowngradedError as e:
            logger.exception(e)
            self.__quick_settings_vm.on_switch_secure_core_button(SecureCoreStatusEnum.OFF, True)
            self.__quick_settings_vm.on_switch_netshield_button(NetshieldTranslationEnum.DISABLED, True)
            result = dt.DisplayDialog(
                title="Downgraded Account",
                text="Your subscription has been downgraded, "
                "so we are reconnecting to the fastest available server."
            )
            self.state.on_next(result)
            self.connect(ConnectionTypeEnum.FASTEST)
            self.__server_list_vm.on_load_servers()
            return
        except exceptions.VPNUsernameOrPasswordHasBeenChangedError as e:
            logger.exception(e)
            self.connect(connection_type_enum, extra_arg, reconnect)
            return
        except exceptions.AccountPasswordHasBeenCompromisedError as e:
            logger.exception(e)
            reason_message = str(e)
        except exceptions.ExceededAmountOfConcurrentSessionsError as e:
            logger.exception(e)
            reason_message = "\nPlease disconnect another device to connect this one or upgrade to PLUS " \
                "to get up to 10 devices connected at the same time at https://account.protonvpn.com/dashboard"
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            reason_message = str(e)
        else:
            logger.info("Dbus response: {}".format(connect_response))
            state = connect_response[ConnectionStartStatusEnum.STATE]

        # step 3
        try:
            if state == VPNConnectionStateEnum.IS_ACTIVE:
                result = self._get_connected_state()
            else:
                try:
                    reason_message = self._conn_reason_msg[
                        connect_response[ConnectionStartStatusEnum.REASON]
                    ]
                except: # noqa
                    pass

                result = dt.ConnectError(
                    reason_message,
                    display_troubleshoot_dialog
                )
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            result = dt.DisplayDialog(
                title="Unable to get Connection Data",
                text=str(e)
            )

        self.state.on_next(result)

    def __display_connection_information_during_connect(self, server):
        connection_metadata = protonvpn.get_connection_metadata()
        protocol = connection_metadata[ConnectionMetadataEnum.PROTOCOL.value]
        result = dt.ConnectInProgressInfo(
            entry_country=protonvpn.get_country().get_country_name(
                server.entry_country
            ),
            exit_country=protonvpn.get_country().get_country_name(
                server.exit_country
            ),
            city=server.city,
            servername=server.name,
            protocol=protocol.upper(),
            is_secure_core=FeatureEnum.SECURE_CORE in server.features
        )

        logger.info("Displaying connection information")
        self.state.on_next(result)

    def on_disconnect(self):
        """On disconnect method.

        Ideally the on_disconnect() method should be run
        within a python thread, but is not done so due to
        the reasons specified in class docstring.
        """
        self.state.on_next(dt.Loading())
        result = self._get_not_connected_state()

        try:
            protonvpn.disconnect()
        except (exceptions.ConnectionNotFound, AttributeError):
            pass

        self.state.on_next(result)
        return False

    def _get_connected_state(self):
        """Get connected state.

        Returns:
            ConnectedToVPNInfo
        """
        connection_status = protonvpn.get_connection_status()
        server = connection_status[
            ConnectionStatusEnum.SERVER_INFORMATION
        ]
        countries = [server.exit_country]
        if FeatureEnum.SECURE_CORE in server.features:
            countries.append(server.entry_country)

        result = dt.ConnectedToVPNInfo(
            protocol=connection_status[ConnectionStatusEnum.PROTOCOL],
            servername=server.name,
            countries=countries,
            city=server.city,
            ip=connection_status[ConnectionStatusEnum.SERVER_IP],
            load=str(int(server.load)),
            entry_country_code=server.entry_country,
            exit_country_code=server.exit_country
        )

        return result

    def _get_not_connected_state(self, force=False):
        """Get not connected state.

        Returns:
            ConnectedToVPNInfo
        """
        ip = self.__none_vpn_ip
        isp = self.__none_vpn_isp
        country_code = self.__none_vpn_contry_code

        if ip is None and isp is None and country_code is None or force:
            try:
                location = protonvpn.get_session().get_location_data()
                ip = location.ip
                isp = location.isp
                country_code = location.country_code
                self.__none_vpn_ip = ip
                self.__none_vpn_isp = isp
                self.__none_vpn_contry_code = country_code
            except Exception as e:
                logger.exception(e)

        result = dt.NotConnectedToVPNInfo(
            ip=ip,
            isp=isp,
            country=country_code,
            perma_ks_enabled=protonvpn.get_settings().killswitch == KillswitchStatusEnum.HARD
        )

        return result

    def get_quick_settings_state(self):
        settings = protonvpn.get_settings()
        state = dt.QuickSettingsStatus(
            secure_core=self.sc_quick_setting[settings.secure_core],
            netshield=self.ns_quick_setting[settings.netshield],
            killswitch=self.ks_quick_setting[settings.killswitch],
        )
        return state

    def on_monitor_vpn_async(self):
        """Start VPN connection monitor.

        Since the VPN can be enabled via CLI,
        it should constantly monitor for an active
        protonvpn connection created by the library.

        The main method is started within a background process
        so that the UI will not freeze.

        Since it is being invoked via a GLib method, it returns True
        so that the method can be called again. If returned False,
        then the callback would stop.
        """
        process = BackgroundProcess.factory("gtask")
        process.setup(self.__on_monitor_vpn)
        process.start()
        return True

    def __on_monitor_vpn(self, *_):
        """Monitor VPN connection.

        This methods monitors a VPN connection state from withing
        a thread. It is mainly used to track when a VPN connection
        is stopped and/or removed.
        """
        result = None
        try:
            protonvpn_connection = protonvpn\
                .get_active_protonvpn_connection()
        except: # noqa
            result = self._get_not_connected_state()
        else:
            try:
                if not protonvpn_connection:
                    result = self._get_not_connected_state()
                else:
                    result = self._get_connected_state()
            except (exceptions.ProtonVPNException, Exception) as e:
                logger.exception(e)

        if result:
            self.state.on_next(result)

    def on_update_speed_async(self):
        """Update network speed.

        The main method is started within a python thread
        so that the UI does not freeze up.

        Since it is being invoked via a GLib method, it returns True
        so that the method can be called again. If returned False,
        then the callback would stop.
        """
        process = BackgroundProcess.factory("gtask")
        process.setup(self.__on_update_speed)
        process.start()
        return True

    def __on_update_speed(self, *_):
        """Updates UI with current network speed.

        This method is and should be executed within a python thread,
        so that it does not freeze the UI due to the constant
        UI updates.
        """
        speed_result = self.utils.get_network_speed()
        up, dl = "-", "-"
        if len(speed_result) == 2:
            up, dl = str(speed_result[0]), str(speed_result[1])
        result = dt.NetworkSpeed(
            download=dl,
            upload=up
        )
        self.state.on_next(result)
