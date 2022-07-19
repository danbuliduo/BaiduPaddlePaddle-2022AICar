#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time

from widgets import startmachine, Buzzer

if __name__ == "__main__":
    startmachine()
    b = Buzzer()
    b.rings()
    time.sleep(0.1)
