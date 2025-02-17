from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence, Tuple
import sys

TAX_YEAR = 2024
TAX_BRACKETS = (
    (23200, 0.10),
    (94300, 0.12),
    (201050, 0.22),
    (383900, 0.24),
    (487450, 0.32),
    (731200, 0.35),
    (sys.maxsize, 0.37))
STD_DEDUCTION = 30000
CG_TAX_BRACKETS = (
  (94050, 0),
  (583750, 0.15),
  (sys.maxsize, 0.2))

@dataclass
class TaxRate:
  inflation: float
  brackets:Sequence=TAX_BRACKETS
  standard_deduction:int=STD_DEDUCTION
  cg_brackets:Sequence=CG_TAX_BRACKETS
  year:int=TAX_YEAR

  def annual(self, ordinary_income:float, cg_income: float, current_year) -> Mapping[str,Any]:
    def _inflate(value:float, year_index)->float:
      return value*(1+self.inflation)**year_index
    std_ded = _inflate(self.standard_deduction, current_year-self.year)
    adjusted_gross_income = ordinary_income + cg_income
    ni=0
    tax_due = 0
    if std_ded < adjusted_gross_income:
      taxable_income = adjusted_gross_income - std_ded
      taxable_ordinary_income = taxable_income - cg_income
      prev_level = 0
      for level,rate in self.brackets:
        level = _inflate(level, current_year-self.year)
        level_income = min(level, taxable_ordinary_income)-prev_level
        tax_due += level_income * rate
        if taxable_ordinary_income <=level:
          break
        prev_level = level
      remaining_cg_income = cg_income
      for level,rate in self.cg_brackets:
        level = _inflate(level, current_year-self.year)
        if remaining_cg_income:
          level_cg_income = min(remaining_cg_income, max(0,level - taxable_ordinary_income))
          tax_due += rate * level_cg_income
          remaining_cg_income -= level_cg_income
        else:
          break
    return dict(year=current_year,tax=tax_due)