"""
mbed SDK
Copyright (c) 2018 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sysctl
import re

from .lstools_base import MbedLsToolsBase

import logging
logger = logging.getLogger("mbedls.lstools_freebsd")
logger.addHandler(logging.NullHandler())
del logging


class MbedLsToolsFreeBSD(MbedLsToolsBase):
    """ mbed-enabled platform for FreeBSD
    """
    def __init__(self, **kwargs):
        """! ctor
        """
        MbedLsToolsBase.__init__(self, **kwargs)

    def find_candidates(self):

        modems = self._find_umodem()
        return modems

    def _find_umodem(self):
        umodems = []
        for i in range(0, 10):
            umodem = sysctl.filter('dev.umodem.%d' % i)
            if umodem == []:
                continue
            location = sysctl.filter('dev.umodem.{0}.%location'.format(i))[0].value
            pnpinfo = sysctl.filter('dev.umodem.{0}.%pnpinfo'.format(i))[0].value
            tty = sysctl.filter('dev.umodem.{0}.ttyname'.format(i))[0].value
            m = re.search('.*ugen=(.*)', location)
            ugen = m.group(1)
            m = re.search('.*vendor=(0x[0-F]*).*', pnpinfo)
            vendor = m.group(1)
            m = re.search('.*product=(0x[0-F]*).*', pnpinfo)
            product = m.group(1)

            serial = ''
            # Find the disk based on ugen value
            for i in range(0, 10):
                umass = sysctl.filter('dev.umass.%d' % i)
                if umass == []:
                    break
                umass_location = sysctl.filter('dev.umass.{0}.%location'.format(i))[0].value
                m = re.search('.*ugen=(.*)', umass_location)
                umass_ugen = m.group(1)
                if umass_ugen != ugen:
                    continue
                umass_pnpinfo = sysctl.filter('dev.umodem.{0}.%pnpinfo'.format(i))[0].value
                m = re.search('.*sernum="([0-F]*)".*', umass_pnpinfo)
                serial = m.group(1)

            if serial == '':
                continue

            umodems.append(
                {'serial_port': 'cua{0}'.format(tty),
                 'vendor_id': vendor,
                 'product_id': product,
                 'location': ugen,
                 'target_id_usb_id' : serial,
                 'mount_point' : '/media/mbed/{0}'.format(serial),
                })
        return umodems
