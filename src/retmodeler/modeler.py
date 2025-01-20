
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from retmodeler.asset import Asset
from retmodeler.expense import Expense

@dataclass
class Model:
  birth_year:int
  assets: Sequence[Asset]
  expenses: Sequence[Expense]
  ret_start_year: int

  def simulate(self, plan_to_age):
    duration = plan_to_age - (self.ret_start_year - self.birth_year)
    yearly_values = {a.name:np.ndarray(duration) for a in self.assets}
    for e in self.expenses:
      yearly_values[e.name] = np.ndarray(duration)
    yearly_values['deficit'] = np.ndarray(duration)

    for i in range(duration):
      for a in self.assets:
        yearly_values[a.name][i] = a.amount
      for e in self.expenses:
        yearly_values[e.name][i] = e.amount

      for a in self.assets:
        a.annual()
      for e in self.expenses:
        deficit = e.annual()
        yearly_values['deficit'][i] = deficit
    return pd.DataFrame(yearly_values, index=range(self.ret_start_year, self.ret_start_year+duration))
