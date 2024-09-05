#!/usr/bin/env python3
import time

import gpiod
from gpiod.line import Direction, Value

#LINE = 73
TRG_LINES = [73, 228, 229]
SAMPLE_WAIT = 0.1


with gpiod.request_lines(
    "/dev/gpiochip0",
    consumer="trg-example",
    config={
        tuple(TRG_LINES): gpiod.LineSettings(
        #LINE: gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.ACTIVE
        )
    },
) as request:
    for line in TRG_LINES:
        request.set_value(line, Value.INACTIVE)
        time.sleep(SAMPLE_WAIT)
        print(f'  UP {line}')
        request.set_value(line, Value.ACTIVE)
        #time.sleep(0.0001)
        time.sleep(0.001)
        request.set_value(line, Value.INACTIVE)
        print(f'FINISH {line}')
        time.sleep(SAMPLE_WAIT)

    """
    request.set_value(LINE, Value.INACTIVE)
    time.sleep(SAMPLE_WAIT)
    request.set_value(LINE, Value.ACTIVE)
    time.sleep(0.0001)
    request.set_value(LINE, Value.INACTIVE)
    time.sleep(sample_wait)
    """
