import unittest

from state_machine import StateMachine, TransitionError


class StateMachineTest(unittest.TestCase):
    def _turnstile(self):
        """A small, real machine: locked -> pushed -> unlocked -> pushed -> locked."""
        return StateMachine(
            states=["locked", "unlocked"],
            initial="locked",
            transitions=[
                ("locked", "coin", "unlocked"),
                ("unlocked", "push", "locked"),
                ("locked", "push", "locked"),
            ],
        )

    def test_initial_state_is_set(self):
        m = self._turnstile()
        self.assertEqual(m.current_state, "locked")

    def test_trigger_returns_new_state(self):
        m = self._turnstile()
        result = m.trigger("coin")
        self.assertEqual(result, "unlocked")
        self.assertEqual(m.current_state, "unlocked")

    def test_trigger_follows_declared_path(self):
        m = self._turnstile()
        m.trigger("coin")
        m.trigger("push")
        self.assertEqual(m.current_state, "locked")

    def test_undeclared_transition_raises_and_keeps_state(self):
        m = self._turnstile()
        # "coin" is valid from "locked" but not from "unlocked".
        m.trigger("coin")
        self.assertEqual(m.current_state, "unlocked")
        with self.assertRaises(TransitionError) as ctx:
            m.trigger("coin")
        # State must be unchanged after the failed trigger.
        self.assertEqual(m.current_state, "unlocked")
        self.assertIn("unlocked", str(ctx.exception))

    def test_event_with_no_transition_from_any_state_raises(self):
        m = self._turnstile()
        with self.assertRaises(TransitionError):
            m.trigger("kick")

    def test_can_trigger_true_for_valid_event(self):
        m = self._turnstile()
        self.assertTrue(m.can_trigger("coin"))
        self.assertTrue(m.can_trigger("push"))

    def test_can_trigger_false_for_invalid_event_from_current_state(self):
        m = self._turnstile()
        # "coin" is only valid from "locked", not from "unlocked".
        m.trigger("coin")
        self.assertFalse(m.can_trigger("coin"))

    def test_can_trigger_does_not_mutate_state(self):
        m = self._turnstile()
        m.can_trigger("coin")
        self.assertEqual(m.current_state, "locked")

    def test_initial_not_in_states_raises_value_error(self):
        with self.assertRaises(ValueError):
            StateMachine(states=["a", "b"], initial="c", transitions=[])

    def test_empty_states_raises_value_error(self):
        with self.assertRaises(ValueError):
            StateMachine(states=[], initial="x", transitions=[])

    def test_transition_from_undeclared_state_raises_value_error(self):
        with self.assertRaises(ValueError):
            StateMachine(
                states=["a", "b"],
                initial="a",
                transitions=[("x", "go", "b")],
            )

    def test_transition_to_undeclared_state_raises_value_error(self):
        with self.assertRaises(ValueError):
            StateMachine(
                states=["a", "b"],
                initial="a",
                transitions=[("a", "go", "z")],
            )

    def test_duplicate_transition_last_definition_wins(self):
        m = StateMachine(
            states=["a", "b", "c"],
            initial="a",
            transitions=[
                ("a", "go", "b"),
                ("a", "go", "c"),
            ],
        )
        self.assertEqual(m.trigger("go"), "c")

    def test_malformed_transition_tuple_raises_value_error(self):
        with self.assertRaises(ValueError):
            StateMachine(
                states=["a"],
                initial="a",
                transitions=[("a", "go")],
            )

    def test_self_transition_allowed(self):
        m = StateMachine(
            states=["a", "b"],
            initial="a",
            transitions=[("a", "tick", "a")],
        )
        self.assertEqual(m.trigger("tick"), "a")

    def test_reset_to_initial_state(self):
        m = StateMachine(
            states=["a", "b"],
            initial="a",
            transitions=[("a", "go", "b")],
        )
        m.trigger("go")
        self.assertEqual(m.current_state, "b")
        m.reset()
        self.assertEqual(m.current_state, "a")

    def test_reset_to_explicit_state(self):
        m = StateMachine(
            states=["a", "b", "c"],
            initial="a",
            transitions=[
                ("a", "go", "b"),
                ("b", "go", "c"),
            ],
        )
        m.trigger("go")
        m.trigger("go")
        m.reset("b")
        self.assertEqual(m.current_state, "b")

    def test_reset_to_undeclared_state_raises_value_error(self):
        m = StateMachine(
            states=["a", "b"],
            initial="a",
            transitions=[("a", "go", "b")],
        )
        with self.assertRaises(ValueError):
            m.reset("z")

    def test_states_property_returns_frozenset(self):
        m = self._turnstile()
        self.assertEqual(m.states, frozenset({"locked", "unlocked"}))

    def test_states_property_is_immutable(self):
        m = self._turnstile()
        # A frozenset has no .add; this exercises the type rather than
        # merely asserting equality.
        with self.assertRaises(AttributeError):
            m.states.add("extra")

    def test_repr_shows_current_state_and_states(self):
        m = self._turnstile()
        text = repr(m)
        self.assertIn("StateMachine", text)
        self.assertIn("locked", text)


if __name__ == "__main__":
    unittest.main()
