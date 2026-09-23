import json
from typing import List
from src.models import LogEvent

def parse(log_file: str) -> List[LogEvent]:
    log_events = []
    with open(log_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            log_events.append(LogEvent(data))
    return log_events
