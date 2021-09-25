from dataclasses import dataclass
from enum import Enum, auto
from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib import exceptions
from ..rx.subject.replaysubject import ReplaySubject
from ..logger import logger
from protonvpn_nm_lib.enums import KillswitchStatusEnum
from ..patterns.factory import BackgroundProcess
from .dataclass.login import *


class LoginViewModel:

    def __init__(self):
        self.user_settings = protonvpn.get_settings()
        self.state = ReplaySubject(buffer_size=1)
        self.__username = None
        self.__password = None

    def login_async(self, username, password):
        self.__username = username
        self.__password = password

        self.state.on_next(LoginState.IN_PROGRESS)
        process = BackgroundProcess.factory("gtask")
        process.setup(self.__login)
        process.start()

    def __login(self, *_):
        result = None
        connection_error = False
        display_troubleshoot_dialog = False

        try:
            protonvpn.login(self.__username, self.__password)
            result = LoginState.SUCCESS
        except exceptions.InsecureConnection as e:
            logger.exception(e)
            connection_error = "Your connection is not secure. " \
                "Please change network and attempt a new connection."
            display_troubleshoot_dialog = True
        except exceptions.APITimeoutError as e:
            logger.exception(e)
            connection_error = "Connection to API timed out."
            display_troubleshoot_dialog = True
        except exceptions.UnreacheableAPIError as e:
            logger.exception(e)
            connection_error = "Unable to reach API"
            display_troubleshoot_dialog = True
        except exceptions.APIError as e:
            logger.exception(e)
            connection_error = "Error in reaching API."
            display_troubleshoot_dialog = True
        except exceptions.NetworkConnectionError as e:
            logger.exception(e)
            connection_error = "Network Error"
            display_troubleshoot_dialog = True
        except exceptions.UnknownAPIError as e:
            logger.exception(e)
            connection_error = "Unknown API error."
        except (
            exceptions.API8002Error, exceptions.API5002Error,
            exceptions.API5003Error
        ) as e:
            logger.exception(e)
            connection_error = str(e)
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            connection_error = "Unknown error occurred. If the issue persists, " \
                "please contact support."

        if connection_error:
            result = LoginError(
                connection_error,
                display_troubleshoot_dialog
            )

        self.state.on_next(result)

    def is_killswitch_enabled(self):
        """Check if kill switch is enabled or not.

        Returns:
            bool
        """
        if self.user_settings.killswitch == KillswitchStatusEnum.HARD:
            return True

        return False

    def disable_killswitch(self):
        """Disable kill switch."""
        try:
            self.user_settings.killswitch = KillswitchStatusEnum.DISABLED
        except Exception as e:
            logger.exception(e)
