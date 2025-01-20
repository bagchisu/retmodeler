from dataclasses import dataclass
from typing import Sequence, Tuple
import sys

@dataclass
class TaxRate:
  brackets: Sequence[Tuple[int, float]]
  year:int
  inflation: float

  def tax(self, taxable_income:float, current_year):
    def _inflate(b, year_index):
      return b[0]*(1+self.inflation)**year_index,b[1]
    prev_level = 0
    tax_due = 0
    for b in self.brackets:
      level,rate = _inflate(b, current_year-self.year)
      level_income = min(level, taxable_income)-prev_level
      tax_due += level_income * rate
      if taxable_income <=level:
        return tax_due
      prev_level = level
      
if __name__ == '__main__':
  tax_rate = TaxRate([
    (23200, 0.10),
    (94300, 0.12),
    (201050, 0.22),
    (383900, 0.24),
    (487450, 0.32),
    (731200, 0.35),
    (sys.maxsize, 0.37)
    ], 2024, 0.03)
  print(tax_rate.tax(100000, 2024))