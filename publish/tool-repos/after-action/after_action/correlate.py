"""Explainable event-to-decision correlation."""

from __future__ import annotations

from dataclasses import dataclass

from .adapters import Decision, Event


@dataclass(frozen=True)
class Link:
    event: Event
    decision: Decision
    signed_delta_seconds: int
    absolute_delta_seconds: int
    reason: str


@dataclass(frozen=True)
class CorrelationResult:
    events: list[Event]
    decisions: list[Decision]
    links: list[Link]
    unlinked_events: list[Event]
    unlinked_decisions: list[Decision]
    window_seconds: int


def correlate(events: list[Event], decisions: list[Decision], window_seconds: int) -> CorrelationResult:
    if window_seconds <= 0:
        raise ValueError("correlation window must be positive")
    links: list[Link] = []
    linked_events: set[Event] = set()
    linked_decisions: set[Decision] = set()
    for event in events:
        for decision in decisions:
            if event.asset != decision.asset:
                continue
            signed = int((decision.timestamp - event.timestamp).total_seconds())
            absolute = abs(signed)
            if absolute <= window_seconds:
                links.append(Link(event, decision, signed, absolute,
                                  f"exact normalized asset; within ±{window_seconds} seconds"))
                linked_events.add(event)
                linked_decisions.add(decision)
    links.sort(key=lambda item: (item.event.timestamp, item.decision.timestamp,
                                 item.event.source, item.decision.source))
    return CorrelationResult(
        events=sorted(events, key=lambda item: (item.timestamp, item.source)),
        decisions=sorted(decisions, key=lambda item: (item.timestamp, item.source)),
        links=links,
        unlinked_events=[item for item in events if item not in linked_events],
        unlinked_decisions=[item for item in decisions if item not in linked_decisions],
        window_seconds=window_seconds,
    )
