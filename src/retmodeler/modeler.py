
from collections import defaultdict
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from retmodeler.asset import Asset
from retmodeler.income import Income
from retmodeler.expense import Expense,CalculatedExpense
from retmodeler.tax import TaxRate

@dataclass
class Model:
  birth_year:int
  ret_start_year: int
  assets: Sequence[Asset]
  incomes: Sequence[Income]
  expenses: Sequence[Expense]
  tax_rate: TaxRate
  tax_expense:CalculatedExpense

  def __post_init__(self):
    self.yearly_income_statements = defaultdict(list)
    self.yearly_asset_statements = defaultdict(list)
    self.yearly_expense_statements = defaultdict(list)
    self.yearly_tax_statements = defaultdict(list)

  def simulate(self, plan_to_age):
    taxable_income = 0
    cg_taxable_income = 0
    for y in range(self.ret_start_year, self.birth_year+plan_to_age):
      # calculate and withdraw last year's taxes
      statement = self.tax_rate.annual(taxable_income, cg_taxable_income, y-1)
      self.yearly_tax_statements[y-1].append(statement)
      tax=statement['tax']
      deficit = self.tax_expense.annual(y, tax)
      taxable_income = 0
      cg_taxable_income = 0
      # get and deposit the incomes
      for i in self.incomes:
        statement = i.annual(y)
        taxable_income += statement['taxable_income']
        self.yearly_income_statements[y].append(statement)
      # calculate and withdraw this year's expenses
      for e in self.expenses:
        deficit += e.annual(y)
        self.yearly_expense_statements[e.name].append(e.amount)
      # calculate and add this year's taxable withdrawals and asset growth
      for a in self.assets:
        statement = a.annual(y, self.birth_year)
        taxable_income += statement['taxable_withdrawals']
        cg_taxable_income += statement['taxable_capital_gains']
        self.yearly_asset_statements[y].append(statement)
    return 

  def taxes_paid(self):
    return self.total_taxes_paid
  
  def asset_worth(self):
    return sum([a.amount for a in self.assets])