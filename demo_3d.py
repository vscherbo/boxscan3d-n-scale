#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: 2023 Kent Gibson <warthog618@gmail.com>

"""Minimal example of watching for rising edges on a single line."""

import time

from datetime import timedelta
import gpiod

from gpiod.line import Edge


def edge_type_str(event):
    if event.event_type is event.Type.RISING_EDGE:
        return "Rising"
    if event.event_type is event.Type.FALLING_EDGE:
        return "Falling"
    return "Unknown"

def watch_lines_edge(chip_path, line_def):
    print(f'{line_def}')
    line_offsets = []
    for line_num in line_def.keys():
        line_offsets.append(line_num)
    print(f'{line_offsets}')

    with gpiod.request_lines(
        chip_path,
        consumer="watch-lines-edge",
        config={tuple(line_offsets): gpiod.LineSettings(edge_detection=Edge.BOTH, debounce_period=timedelta(microseconds=0))},
    ) as request:
        ts_ns = {}
        dist3 = {}
        for line in line_offsets:
           ts_ns[line] = {}
           dist3[line] = []
        print(f'start. {ts_ns}')
        while True:
            # Blocks until at least one event is available
            for event in request.read_edge_events():
                """
                print(
                        "line: {}  type: {:<7}   event #{} line event #{}".format(
                        event.line_offset,
                        line_def[event.line_offset]['name'],
                        edge_type_str(event), 
                        #event.event_type,
                        event.global_seqno,
                        event.line_seqno
                    )
                )
                """
                #if event.event_type == gpiod.edge_event.EdgeEvent.Type.RISING_EDGE:
                if event.event_type == event.Type.RISING_EDGE:
                    ts_ns[event.line_offset]['rising'] = event.timestamp_ns
                    #print(f'ts_ns={ts_ns}')
                if event.event_type == event.Type.FALLING_EDGE:
                    try:
                        ts_delta = event.timestamp_ns - ts_ns[event.line_offset]['rising']
                        #print(f'delta={ts_delta}')
                        #dist_cm = round(ts_delta/1000/58.8, 1)
                        dist_cm = round(ts_delta/1000/57.72, 1)
                        print(f'   {line_def[event.line_offset]["name"]}', f'dist(cm)={dist_cm}')
                        dist3[event.line_offset].append(dist_cm)
                        if len(dist3[event.line_offset]) == 2:
                            dist_avg = round((dist3[event.line_offset][0] + dist3[event.line_offset][1])/2.0, 1)
                            dist3[event.line_offset] = []
                            size = round(line_def[event.line_offset]['base'] - dist_avg, 1)
                            print(f'{line_def[event.line_offset]["name"]}', f'dist_avg={dist_avg}', f'size={size}')
                        ts_ns[event.line_offset] = {}
                    except KeyError:
                        print('NO rising. Skip')
                #print(event)


if __name__ == "__main__":
    try:
        #watch_line_edge("/dev/gpiochip0", 75)  # P1 23-25cm BAD, real 48cm
        #watch_line_edge("/dev/gpiochip0", 69)  # P2 46cm BAD, real 85cm
        #watch_line_edge("/dev/gpiochip0", 79)  # P4 32-34cm, real 35cm
        line_def = {}
        line_def[79] = {'name': 'высота', 'base': 34}  # 35?
        line_def[75] = {'name': 'ширина', 'base': 47}  # 48?
        line_def[69] = {'name': 'длина', 'base': 85}

        watch_lines_edge("/dev/gpiochip0", line_def)
        #watch_lines_edge("/dev/gpiochip0", [69, 75, 79])
    except OSError as ex:
        print(ex, "\nCustomise the example configuration to suit your situation")
