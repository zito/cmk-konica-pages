#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# CheckMK plugin to show Konica Minolta print counters according to 
# https://community.lansweeper.com/t5/general-discussions/konica-minolta-print-counters/td-p/50443
#
#  copy counter black  (1.3.6.1.4.1.18334.1.1.1.5.7.2.2.1.5.1.1)
#  print counter black (1.3.6.1.4.1.18334.1.1.1.5.7.2.2.1.5.1.2)
#  copy counter color  (1.3.6.1.4.1.18334.1.1.1.5.7.2.2.1.5.2.1)
#  print counter color (1.3.6.1.4.1.18334.1.1.1.5.7.2.2.1.5.2.2)
#  total counter       (1.3.6.1.4.1.18334.1.1.1.5.7.2.1.1.0)
#  scans               (1.3.6.1.4.1.18334.1.1.1.5.7.2.1.5.0)

from typing import List

from cmk.agent_based.v2 import (
    all_of,
    CheckPlugin,
    exists,
    SNMPSection,
    SNMPTree,
    startswith,
    StringTable,
)

from cmk.plugins.lib.printer import (
    check_printer_pages_types,
    discovery_printer_pages,
    OID_sysObjectID,
    Section,
)


DETECT_KONICA_HAS_TOTAL = all_of(
    startswith(OID_sysObjectID, ".1.3.6.1.4.1.18334"),
    exists(".1.3.6.1.4.1.18334.1.1.1.5.7.2.2.1.5.*"),
    exists(".1.3.6.1.4.1.18334.1.1.1.5.7.2.1.1.0"),
)

def parse_printer_pages_konica(string_table: List[StringTable]) -> Section:
    (copy_black, print_black, copy_color, print_color) = string_table[0][0]
    (total, ) = string_table[1][0]
    parsed = {}
    try:
        copy_black = int(copy_black)
        print_black = int(print_black)
        if copy_black < 0:
            copy_black = 0
        if print_black < 0:
            print_black = 0
        parsed["pages_bw"] = copy_black + print_black
    except:
        pass
    try:
        copy_color = int(copy_color)
        print_color = int(print_color)
        if copy_color < 0:
            copy_color = 0
        if print_color < 0:
            print_color = 0
        parsed["pages_color"] = copy_color + print_color
    except:
        pass
    try:
        parsed["pages_total"] = int(total)
    except:
        pass
    return parsed


snmp_section_konica_pages = SNMPSection(
    name="konica_pages",
    detect=DETECT_KONICA_HAS_TOTAL,
    supersedes=["printer_pages"],
    parse_function=parse_printer_pages_konica,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.18334.1.1.1.5.7.2.2.1.5",
            oids=[
                "1.1",
                "1.2",
                "2.1",
                "2.2",
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.18334.1.1.1.5.7.2.1",
            oids=[
                "1.0",
            ],
        ),
    ],
)

check_plugin_konica_pages = CheckPlugin(
    name="konica_pages",
    service_name="Pages",
    discovery_function=discovery_printer_pages,
    check_function=check_printer_pages_types,
)
