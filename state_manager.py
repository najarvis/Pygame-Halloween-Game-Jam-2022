

class State:

    def __init__(self, name: str):
        self.name = name

    def entry_actions(self) -> None:
        """What should happen once when the state is reached"""
        NotImplemented

    def exit_actions(self) -> None:
        """What should happen when leaving this state"""
        NotImplemented

    def do_actions(self) -> None:
        """What should happen while the state is active"""
        NotImplemented

    def check_conditions(self) -> str | None:
        """Check certain conditions, if this function returns a string go to that state."""
        return None
    
class StateManager:

    def __init__(self):
        self.states: dict[str, State] = {}
        self.active_state: State = None

    def add_state(self, new_state: State) -> None:
        if new_state in self.states:
            raise Exception(f"State `{new_state.name}` already exists in StateManager")
        
        self.states[new_state.name] = new_state

    def do_state(self) -> None:
        if self.active_state is None:
            return

        self.active_state.do_actions()

        new_state_name = self.active_state.check_conditions()
        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, new_state_name: str) -> None:
        if new_state_name not in self.states:
            raise Exception(f"State `{new_state_name}` not in the list of available states.")

        if self.active_state is not None:
            self.active_state.exit_actions()

        self.active_state = self.states[new_state_name]
        self.active_state.entry_actions()
