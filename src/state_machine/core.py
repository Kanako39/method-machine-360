from __future__ import annotations


class TransitionError(ValueError):
    """Raised when an event is triggered for which no transition exists.

    Subclassing :class:`ValueError` keeps the exception hierarchy shallow
    while still letting callers catch transition failures specifically
    without also swallowing unrelated programming errors.
    """


class StateMachine:
    """A finite state machine that rejects undeclared transitions.

    Example:
        >>> m = StateMachine(
        ...     states=["idle", "running", "done"],
        ...     initial="idle",
        ...     transitions=[
        ...         ("idle", "start", "running"),
        ...         ("running", "finish", "done"),
        ...     ],
        ... )
        >>> m.trigger("start")
        'running'
        >>> m.current_state
        'running'
        >>> m.trigger("finish")
        'done'

    Args:
        states: Iterable of state names. Duplicates are collapsed; the
            order is not significant.
        initial: The state the machine starts in. Must be present in
            ``states``.
        transitions: Iterable of ``(from_state, event, to_state)`` tuples.
            Both states must appear in ``states``. Multiple transitions
            may share the same ``(from_state, event)`` pair; the last one
            in iteration order wins. This "last definition wins" rule is
            documented rather than forbidden so a caller can override an
            earlier declaration deliberately.

    Raises:
        ValueError: If ``initial`` is not a declared state, or if a
            transition references an undeclared state.
    """

    def __init__(self, states, initial, transitions):
        # A set gives O(1) membership checks; sorting here would be
        # cosmetic only and would hide the caller's declaration order
        # during error messages, so we do not sort.
        state_set = set(states)
        if not state_set:
            raise ValueError("states must contain at least one state")
        if initial not in state_set:
            raise ValueError(
                "initial state %r is not in declared states %r"
                % (initial, sorted(state_set))
            )

        # Keyed by (from_state, event). A plain dict preserves "last wins"
        # semantics for duplicate keys for free, which matches the
        # documented behaviour.
        table = {}
        for transition in transitions:
            if len(transition) != 3:
                raise ValueError(
                    "each transition must be a (from_state, event, to_state) tuple, "
                    "got %r" % (transition,)
                )
            from_state, event, to_state = transition
            if from_state not in state_set:
                raise ValueError(
                    "transition references undeclared from_state %r"
                    % (from_state,)
                )
            if to_state not in state_set:
                raise ValueError(
                    "transition references undeclared to_state %r"
                    % (to_state,)
                )
            table[(from_state, event)] = to_state

        # Private by convention. Exposing the raw table would let callers
        # mutate it after construction, defeating the point of declaring
        # transitions up front.
        self._states = state_set
        self._table = table
        self._state = initial
        self._initial = initial

    @property
    def current_state(self):
        """The state the machine is currently in."""
        return self._state

    @property
    def states(self):
        """A frozenset of every declared state."""
        return frozenset(self._states)

    def can_trigger(self, event):
        """Return ``True`` if ``event`` has a transition from the current state."""
        return (self._state, event) in self._table

    def trigger(self, event):
        """Apply ``event`` and return the new state.

        Raises:
            TransitionError: If no transition is defined for ``event``
                from the current state. The machine's state is left
                unchanged on failure; a failed transition is not a
                state change.
        """
        key = (self._state, event)
        if key not in self._table:
            raise TransitionError(
                "no transition for event %r from state %r"
                % (event, self._state)
            )
        self._state = self._table[key]
        return self._state

    def reset(self, state=None):
        """Reset the machine to ``state`` (or its initial state if ``None``).

        Useful for reusing a configured machine across independent runs
        without rebuilding the transition table.

        Args:
            state: The state to reset to. If ``None``, resets to the
                initial state supplied at construction.

        Raises:
            ValueError: If ``state`` is not a declared state.
        """
        target = self._initial if state is None else state
        if target not in self._states:
            raise ValueError(
                "cannot reset to undeclared state %r" % (target,)
            )
        self._state = target

    def __repr__(self):
        return "StateMachine(current_state=%r, states=%r)" % (
            self._state,
            sorted(self._states),
        )
