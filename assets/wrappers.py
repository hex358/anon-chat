import time
import json
import os
import sys
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent)
print(sys.path[-1])

last_usage = time.time()
new_usage = last_usage
report_types = json.load(open('base/console_texts.json', 'r'))

def time_refresh():
    last_usage = time.time()

def _report(type, text, user=False, timed=False):
    global last_usage
    new_usage = time.time()
    run_time = new_usage - last_usage
    last_usage = new_usage
    print(f"{report_types[type]} {str(user)+': ' if user else ""}{text} ({round(run_time,3) if timed else ""})")

def _big_report(text):
    print("="*int(20-(len(text)/2)) + text + "="*int(20-(len(text)/2)))
