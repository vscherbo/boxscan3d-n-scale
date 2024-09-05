#!/usr/bin/env python3
import sys
import time

import gpiod
from gpiod.line import Direction, Value

LINE = 69
FACTOR = 0.1


with gpiod.Chip("/dev/gpiochip0") as chip:
    offset = 69
    #for off in sys.argv[2:]:
    #    offsets.append(int(off))

    lines = chip.get_line(offset)
    lines.request(consumer='echo-rising', type=gpiod.LINE_REQ_EV_RISING_EDGE)

    try:
        while True:
            ev_lines = lines.event_wait(sec=1)
            if ev_lines:
                for line in ev_lines:
                    event = line.event_read()
                    print_event(event)
    except KeyboardInterrupt:
        sys.exit(130)
