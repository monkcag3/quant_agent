
from dataclasses import dataclass


@dataclass
class Account:
    available      : float = 0.0
    withdraw_quota : float = 0.0