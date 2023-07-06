import time
import psutil
from protonvpn_nm_lib.constants import VIRTUAL_DEVICE_NAME


one_byte_in_kBs = 0.000976
one_byte_in_mBs = 9.76e-7
one_kilobyte_in_bytes = 1000
one_megabyte_in_bytes = 1024590.163934


class Utilities:

    @staticmethod
    def get_network_speed():
        """Get current network speed.

        It searches for a interface that is defined within the library.

        Returns:
            list
        """
        t0 = time.time()
        interface = VIRTUAL_DEVICE_NAME
        dt = 3
        try:
            counter = psutil.net_io_counters(pernic=True)[interface]
        except KeyError:
            return []
        tot = (counter.bytes_sent, counter.bytes_recv)

        last_tot = tot
        time.sleep(dt)
        try:
            counter = psutil.net_io_counters(pernic=True)[interface]
        except KeyError:
            return []

        t1 = time.time()
        tot = (counter.bytes_sent, counter.bytes_recv)
        ul, dl = [
            (now - last) / (t1 - t0)
            for now, last
            in zip(tot, last_tot)
        ]
        ul = Utilities.convert_network_speed(ul)
        dl = Utilities.convert_network_speed(dl)
        return [ul, dl]

    @staticmethod
    def convert_network_speed(byte_per_second):
        """Convert network speed.

        Converts and return
        the speed easy readable units:
            - Bytes per second
            - Kilobytes per second
            - Megabytes per second

        Args:
            byte_per_second(int|float)

        Returns:
            string
        """
        if byte_per_second <= 0:
            return "0 B/s"

        if (
            byte_per_second >= one_kilobyte_in_bytes
            and byte_per_second < one_megabyte_in_bytes
        ):
            return str(
                round((byte_per_second * one_byte_in_kBs), 1)
            ) + " KB/s"
        elif byte_per_second >= one_megabyte_in_bytes:
            return str(
                round((byte_per_second * one_byte_in_mBs), 1)
            ) + " MB/s"
        else:
            return str(int(byte_per_second)) + " B/s"
