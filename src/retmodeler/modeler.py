
from collections import defaultdict
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from retmodeler.asset import Asset
from retmodeler.expense import Expense,CalculatedExpense
from retmodeler.tax import TaxRate
from retmodeler.rmd import rmd_uniform_lifetime

@dataclass
class Model:
  birth_year:int
  ret_start_year: int
  assets: Sequence[Asset]
  expenses: Sequence[Expense]
  tax_rate: TaxRate
  tax_expense:CalculatedExpense

  def simulate(self, plan_to_age):
    yearly_values = defaultdict(list)
    taxable_income = 0
    cg_taxable_income = 0
    for y in range(self.ret_start_year, self.birth_year+plan_to_age):
      # calculate and withdraw last year's taxes
      tax = self.tax_rate.tax(taxable_income, cg_taxable_income, y-1)
      deficit = self.tax_expense.annual(tax)
      taxable_income = 0
      cg_taxable_income = 0
      # calculate and withdraw this year's expenses
      for e in self.expenses:
        deficit += e.annual()
        yearly_values[e.name].append(e.amount)
      # calculate and add this year's taxable withdrawals and asset growth
      for a in self.assets:
        ti, cgi = a.annual(y-self.birth_year)
        taxable_income += ti
        cg_taxable_income += cgi
        yearly_values[a.name].append(a.amount)
      yearly_values['tax_paid'].append(tax)
      yearly_values['taxable_income'].append(taxable_income)
      yearly_values['deficit'].append(deficit)
    return pd.DataFrame(yearly_values, index=range(self.ret_start_year, self.birth_year+plan_to_age))
