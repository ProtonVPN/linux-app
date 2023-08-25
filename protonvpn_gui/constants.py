import os

from .enums import (DashboardKillSwitchIconEnum, DashboardNetshieldIconEnum,
                    DashboardSecureCoreIconEnum)

APP_VERSION = "1.12.0"
ABSOLUTE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR_PATH = os.path.join(ABSOLUTE_DIR_PATH, "assets")

UI_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "ui")
CSS_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "css")
ICON_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "icons")
IMG_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "img")
FLAGS_DIR_PATH = os.path.join(IMG_DIR_PATH, "flags")

LOGGER_NAME = "protonvpn-gui"


protonvpn_logo = "protonvpn-logo.png"
VPN_TRAY_ON = "vpn-connected"
VPN_TRAY_OFF = "vpn-disconnected"
VPN_TRAY_ERROR = "vpn-no-network"

KILLSWITCH_ICON_SET = {
    DashboardKillSwitchIconEnum.OFF:
        os.path.join(
            ICON_DIR_PATH,
            "kill-switch.imageset/killswitch-off.svg"
        ),
    DashboardKillSwitchIconEnum.OFF_ACTIVE:
        os.path.join(
            ICON_DIR_PATH,
            "kill-switch.imageset/killswitch-off-active.svg"
        ),
    DashboardKillSwitchIconEnum.ON_DEFAULT:
        os.path.join(
            ICON_DIR_PATH,
            "kill-switch.imageset/killswitch-on-default.svg"
        ),
    DashboardKillSwitchIconEnum.ALWAYS_ON_DEFAULT:
        os.path.join(
            ICON_DIR_PATH,
            "kill-switch.imageset/killswitch-always-on-default.svg"
        ),
    DashboardKillSwitchIconEnum.ON_DISABLE:
        os.path.join(
            ICON_DIR_PATH,
            "kill-switch.imageset/killswitch-on-disable.svg"
        ),
    DashboardKillSwitchIconEnum.ALWAYS_ON_DISABLE:
        os.path.join(
            ICON_DIR_PATH,
            "kill-switch.imageset/killswitch-always-on-disable.svg"
        ),
    DashboardKillSwitchIconEnum.ON_ACTIVE:
        os.path.join(
            ICON_DIR_PATH,
            "kill-switch.imageset/killswitch-on-active.svg"
        ),
    DashboardKillSwitchIconEnum.ALWAYS_ON_ACTIVE:
        os.path.join(
            ICON_DIR_PATH,
            "kill-switch.imageset/killswitch-always-on-active.svg"
        ),
}

NETSHIELD_ICON_SET = {
    DashboardNetshieldIconEnum.OFF:
        os.path.join(
            ICON_DIR_PATH,
            "netshield.imageset/netshield-off.svg"
        ),
    DashboardNetshieldIconEnum.OFF_ACTIVE:
        os.path.join(
            ICON_DIR_PATH,
            "netshield.imageset/netshield-off-active.svg"
        ),
    DashboardNetshieldIconEnum.MALWARE_DEFAULT:
        os.path.join(
            ICON_DIR_PATH,
            "netshield.imageset/netshield-malware-default.svg"
        ),
    DashboardNetshieldIconEnum.MALWARE_ADS_DEFAULT:
        os.path.join(
            ICON_DIR_PATH,
            "netshield.imageset/netshield-malware-ad-default.svg"
        ),
    DashboardNetshieldIconEnum.MALWARE_DISABLE:
        os.path.join(
            ICON_DIR_PATH,
            "netshield.imageset/netshield-malware-disable.svg"
        ),
    DashboardNetshieldIconEnum.MALWARE_ADS_DISABLE:
        os.path.join(
            ICON_DIR_PATH,
            "netshield.imageset/netshield-malware-ad-disable.svg"
        ),
    DashboardNetshieldIconEnum.MALWARE_ACTIVE:
        os.path.join(
            ICON_DIR_PATH,
            "netshield.imageset/netshield-malware-active.svg"
        ),
    DashboardNetshieldIconEnum.MALWARE_ADS_ACTIVE:
        os.path.join(
            ICON_DIR_PATH,
            "netshield.imageset/netshield-malware-ad-active.svg"
        ),
}

SECURE_CORE_ICON_SET = {
    DashboardSecureCoreIconEnum.OFF:
        os.path.join(
            ICON_DIR_PATH,
            "secure-core.imageset/secure-core-off.svg"
        ),
    DashboardSecureCoreIconEnum.OFF_ACTIVE:
        os.path.join(
            ICON_DIR_PATH,
            "secure-core.imageset/secure-core-off-active.svg"
        ),
    DashboardSecureCoreIconEnum.ON_DEFAULT:
        os.path.join(
            ICON_DIR_PATH,
            "secure-core.imageset/secure-core-on-default.svg"
        ),
    DashboardSecureCoreIconEnum.ON_DISABLE:
        os.path.join(
            ICON_DIR_PATH,
            "secure-core.imageset/secure-core-on-disable.svg"
        ),
    DashboardSecureCoreIconEnum.ON_ACTIVE:
        os.path.join(
            ICON_DIR_PATH,
            "secure-core.imageset/secure-core-on-active.svg"
        ),
    DashboardSecureCoreIconEnum.CHEVRON:
        os.path.join(
            ICON_DIR_PATH,
            "secure-core.imageset/secure-core-chevrons-active.svg"
        )
}
