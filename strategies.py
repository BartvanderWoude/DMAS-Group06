from abc import ABC, abstractmethod  # Built in. No install needed.
from typing import Dict

class DefaultStrat:
    def __init__(self):
        self.name = "default"
        self.description = "Default agent with all standard strategies"
        self.strat_color = "green"
        self.trust_tactic = "standard"
        self.witness_tactic = "standard"
        self.trust_update_tactic = "standard"

class NoTrustStrat():
    def __init__(self):
        self.name = "notrust"
        self.description = "Agent who doesnt trust his witness"
        self.strat_color = "red"
        self.trust_tactic = "not_trust_witness"
        self.witness_tactic = "standard"
        self.trust_update_tactic = "standard"

class LowTrustStrat():
    def __init__(self):
        self.name = "lowtrust"
        self.description = "Agent who doesnt trust his witness for a 100 percent"
        self.strat_color = "blue"
        self.trust_tactic = "not_trust_witness" 
        self.witness_tactic = "standard"
        self.trust_update_tactic = "standard"
