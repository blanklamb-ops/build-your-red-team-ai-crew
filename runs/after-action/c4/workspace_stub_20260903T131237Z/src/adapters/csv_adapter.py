import csv
from typing import List
from src.models import LogEvent

def parse(log_file: str) -> List[LogEvent]:
    log_events = []
    with open(log_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            log_events.append(LogEvent(row))
    return log_events
