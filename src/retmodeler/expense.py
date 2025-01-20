from dataclasses import dataclass
from enum import Enum
from typing import Sequence
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

  def annual(self):
    need = self.amount
    for source in self.sources:
      if need > source.amount:
        need -= source.amount
        source.amount = 0
      else:
        source.amount -= need
        need = 0
        break
    self.amount += self.amount * self.annual_inflation
    return need