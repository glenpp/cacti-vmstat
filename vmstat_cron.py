#!/usr/bin/env python3
"""
Copyright (C) 2012-2023  Glen Pitt-Pladdy

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


See https://github.com/glenpp/cacti-vmstat

Version 20230701
"""

import sys
import os
import subprocess


VMSTAT_COMMAND = [
    '/usr/bin/vmstat',
    '--unit', 'K',
    '--wide',
    '300', '2',
]
LABELS_EXPECT_BASE = [
    'procs.r', 'procs.b',
    'memory.swpd', 'memory.free', 'memory.buff', 'memory.cache',
    'swap.si', 'swap.so',
    'io.bi', 'io.bo',
    'system.in', 'system.cs',
    'cpu.us', 'cpu.sy', 'cpu.id', 'cpu.wa', 'cpu.st',
]
LABELS_EXTRA = [
    'cpu.gu',   # kvm guest
]


def vmstat_run():
    """Get vmstat data for timeperiod"""
    proc = subprocess.run(
        VMSTAT_COMMAND,
        capture_output=True,
        check=True,
        text=True,
    )
    lines = proc.stdout.splitlines()
    # parse headers
    category_header = lines[0]
    metric_header = lines[1]
    labels = []
    delimiter = 0
    while delimiter is not None:
        delimiter = category_header.find(' ')
        if delimiter < 0:
            delimiter = None
        category = category_header[:delimiter].strip('-')
        metrics = metric_header[:delimiter].split()
        if delimiter:
            category_header = category_header[delimiter + 1:]
            metric_header = metric_header[delimiter + 1:]
        for metric in metrics:
            labels.append(f'{category}.{metric}')
    extras = len(labels) - len(LABELS_EXPECT_BASE)
    labels_expect = LABELS_EXPECT_BASE[:]
    if extras > len(LABELS_EXTRA):
        raise ValueError(f"Got too many labels, output will not match expected snmp items: {labels}")
    if extras > 0:
        labels_expect.extend(LABELS_EXTRA[:extras])
    if labels != labels_expect:
        raise ValueError(f"Did not get expected labels, output will not match expected snmp items: {labels}")
    # parse values
    values = lines[-1].strip().split()
    values += ['U'] * len(LABELS_EXTRA[extras:])
    return values


def memtotal_get():
    """Get total memory in kB"""
    with open('/proc/meminfo', 'rt') as f_mem:
        for line in f_mem:
            if line.startswith('MemTotal:'):
                break
        else:
            raise ValueError("Failed to find line in /proc/meminfo for: MemTotal")
    parts = line.split()
    if parts[2] != 'kB':
        raise ValueError(f"Wrong unit for MemTotal in /proc/meminfo: {parts[2]}")
    return parts[1]


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path to json output>")
        sys.exit(1)
    file_out = sys.argv[1]
    # get data
    vmstat = vmstat_run()
    mem_total = memtotal_get()
    # write file
    file_tmp = f'{file_out}_TMP{os.getpid()}'
    with open(file_tmp, 'wt') as f_out:
        print(mem_total, file=f_out)
        for value in vmstat:
            print(value, file=f_out)
    os.rename(file_tmp, file_out)


if __name__ == '__main__':
    main()
