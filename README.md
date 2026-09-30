# state_machine

A finite state machine that rejects impossible transitions. You declare states and transitions up front; triggering an event that has no declared transition from the current state raises `TransitionError` and leaves the state untouched.

```python
from state_machine import StateMachine, TransitionError

m = StateMachine(
    states=["idle", "running", "done"],
    initial="idle",
    transitions=[
        ("idle", "start", "running"),
        ("running", "finish", "done"),
    ],
)

m.trigger("start")
print(m.current_state)  # "running"

try:
    m.trigger("start")   # "start" is not valid from "running"
except TransitionError:
    pass
```

## Why

Most state machine bugs are transitions that *should* never happen but silently do, or transitions that fail quietly. This library takes the opposite default: every transition must be declared, and anything not declared is an error. There are no entry/exit actions, no hierarchical states, no guard arguments — if you need a guard, check it before calling `trigger`. Keeping the model this small is the point: a tool that does one thing, rather than a framework.

## Edge to know about

If two transitions are declared for the same `(from_state, event)` pair, the **last definition wins**. This is deliberate, so a caller can override an earlier declaration, but it means duplicate transitions are not reported as an error. If that is not what you want, deduplicate your input before constructing the machine.

## Exports

- `StateMachine(states, initial, transitions)` — constructor.
- `StateMachine.current_state` — the current state (read-only property).
- `StateMachine.states` — a `frozenset` of declared states.
- `StateMachine.trigger(event)` — apply `event`, return the new state; raise `TransitionError` if no transition exists.
- `StateMachine.can_trigger(event)` — `True` if `event` is triggerable from the current state.
- `StateMachine.reset(state=None)` — reset to the initial state, or to `state` if given.
- `TransitionError` — raised on impossible transitions; a subclass of `ValueError`.
