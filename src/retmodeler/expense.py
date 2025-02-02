from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence
from retmodeler.asset import Asset

class TimePeriod(Enum):
  ANNUAL = 1
  SEMIANNUAL = 2
  QUARTERLY = 4
  MONTHLY = 12
  BIMONTHLY = 24

@dataclass
class Expense:
  name:str
  amount:float
  sources:Sequence[Asset]
  annual_inflation:float
  period:TimePeriod=TimePeriod.MONTHLY
  discretionary=False

  def annual(self) -> float:
    need = self.amount
    for source in self.sources:
      need = source.sell(need)
      if not need:
        break
    self.amount += self.amount * self.annual_inflation
    return need
  
@dataclass
class CalculatedExpense(Expense):
  def annual(self, expense) -> float:
    self.amount = expense
    return super().annual()