from dataclasses import dataclass
from typing import Sequence, Tuple
import sys

TAX_YEAR = 2024
TAX_BRACKETS = [
    (23200, 0.10),
    (94300, 0.12),
    (201050, 0.22),
    (383900, 0.24),
    (487450, 0.32),
    (731200, 0.35),
    (sys.maxsize, 0.37)
    ]
STD_DEDUCTION = 30000
CG_TAX_BRACKETS = [
  (94050, 0),
  (583750, 0.15),
  (sys.maxsize, 0.2)
]

@dataclass
class TaxRate:
  inflation: float
  brackets=TAX_BRACKETS
  standard_deduction=STD_DEDUCTION
  cg_brackets=CG_TAX_BRACKETS
  year=TAX_YEAR

  def tax(self, taxable_income:float, cg_income: float, current_year):
    def _inflate(value:float, year_index)->float:
      return value*(1+self.inflation)**year_index
    std_ded = _inflate(self.standard_deduction, current_year-self.year)
    if std_ded > taxable_income:
      return 0
    taxable_income -= std_ded
    prev_level = 0
    tax_due = 0
    for level,rate in self.brackets:
      level = _inflate(level, current_year-self.year)
      level_income = min(level, taxable_income)-prev_level
      tax_due += level_income * rate
      if taxable_income <=level:
        break
      prev_level = level
    for level,rate in self.cg_brackets:
      if taxable_income <= level: continue
      tax_due += rate * cg_income
    return tax_due