#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: 2023 Kent Gibson <warthog618@gmail.com>

"""Minimal example of watching for rising edges on a single line."""

from datetime import timedelta
import gpiod

from gpiod.line import Edge


def watch_line_edge(chip_path, line_offset):
    with gpiod.request_lines(
        chip_path,
        consumer="watch-line-edge",
        config={line_offset: gpiod.LineSettings(edge_detection=Edge.BOTH, debounce_period=timedelta(microseconds=0))},
    ) as request:
        ts_ns = {}
        while True:
            # Blocks until at least one event is available
            for event in request.read_edge_events():
                print(
                    "line: {}  type: {}   event #{}".format(
                        event.line_offset, event.event_type , event.line_seqno
                    )
                )
                #if event.event_type == gpiod.edge_event.EdgeEvent.Type.RISING_EDGE:
                if event.event_type == event.Type.RISING_EDGE:
                    ts_ns['rising'] = event.timestamp_ns
                if event.event_type == event.Type.FALLING_EDGE:
                    try:
                        ts_delta = event.timestamp_ns - ts_ns['rising']
                        print(f'delta={ts_delta}')
                        dist_cm = ts_delta/1000/58
                        print(f'dist(cm)={dist_cm}')
                        ts_ns = {}
                    except KeyError:
                        print('NO rising. Skip')
                #print(event)


if __name__ == "__main__":
    try:
        #watch_line_edge("/dev/gpiochip0", 75)  # P1 23-25cm BAD, real 48cm
        watch_line_edge("/dev/gpiochip0", 69)  # P2 46cm BAD, real 85cm
        #watch_line_edge("/dev/gpiochip0", 79)  # P4 32-34cm, real 35cm
    except OSError as ex:
        print(ex, "\nCustomise the example configuration to suit your situation")
