import atexit
import time
from datetime import timedelta

timing_stamps = {}

def timing_end():
    global timing_stamps
    timing_stop = time.monotonic()
    print("*[T]* Timing end: %s" % timedelta(seconds=timing_stop - timing_stamps["_timing_start"]))

def timing_stamp_start(id):
    global stamps
    timing_stamps[id] = time.monotonic()
    print("*[T]* [start] %s" % id)
    
def timing_stamp_end(id):
    global timing_stamps
    timing_stop = time.monotonic()
    print("*[T]* [end  ] %s: %s" % (id,timedelta(seconds=timing_stop - timing_stamps[id])))
    timing_stamps[id] = 0
    

timing_stamps["_timing_start"] = time.monotonic()
atexit.register(timing_end)
print("*[T]* Timing registered")
