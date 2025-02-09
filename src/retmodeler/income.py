from dataclasses import dataclass
from retmodeler.asset import Asset

@dataclass
class Income:
  name: str
  start_amount:float
  start_year:int
  annual_growth: float
  deposit_asset: Asset
  taxable=True
  amount=0


  def annual(self, year):
    taxable_income = 0
    if year == self.start_year:
      self.amount = self.start_amount
    elif year > self.start_year:
      self.amount += self.amount * self.annual_growth
    if self.taxable:
      taxable_income = self.amount
    if self.amount:
      self.deposit_asset.buy(self.amount)
    return taxable_income