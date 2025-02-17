from dataclasses import dataclass
from typing import Any, List, Mapping, Tuple
from retmodeler.asset import Asset

@dataclass
class Income:
  name: str
  start_amount:float
  start_year:int
  annual_growth: float
  reinv_asset:List[Tuple['Asset',float]]
  taxable:bool=True
  amount=0

  def annual(self, year:int)->Mapping[str,Any]:
    taxable_income = 0
    if year == self.start_year:
      self.amount = self.start_amount
    elif year > self.start_year:
      self.amount += self.amount * self.annual_growth
    if self.taxable:
      taxable_income = self.amount
    if self.amount:
      remainder = self.amount
      for a,f in self.reinv_asset:
        a_buy = self.amount * f
        a.buy(year, a_buy)
        remainder -= a_buy
      assert(remainder==0)
    return dict(year=year, name=self.name, amount=self.amount, taxable_income=taxable_income)
  