"""
Finite state machine that rejects impossible transitions.

The module exposes a single :class:`StateMachine` class. States and
transitions are declared up front; any transition that was not declared
raises :class:`TransitionError` rather than silently being accepted or
no-op'd. This is the whole point of the library: making illegal state
changes loud.
"""

from state_machine.core import StateMachine, TransitionError

__all__ = ["StateMachine", "TransitionError"]
