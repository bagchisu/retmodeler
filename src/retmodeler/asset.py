from dataclasses import dataclass
from typing import Any, List, Mapping, Optional, Tuple
import numpy as np

from retmodeler.rmd import rmd_uniform_lifetime

@dataclass
class InvestmentType:
  name:str
  tax_deferred:bool # pay tax on withdrawal as ordinary income
  tax_free:bool # no tax on dividends and capital gain (roth)

INV_BROKERAGE = InvestmentType('brokerage', False, False)
INV_401K = InvestmentType('401k', True, False)
INV_ROTH = InvestmentType('roth', False, True)

@dataclass
class AssetClass:
  name:str
  annual_return:float
  fixed_income:float # if true share price is fixed at $1

@dataclass
class Asset:
  name:str
  amount:float
  cost: float
  investment_type:InvestmentType
  asset_class:AssetClass
  reinv_asset:List[Tuple['Asset',float]]
  savings_asset:Optional['Asset']=None

  def __post_init__(self):
    self.annual_purchases=0
    self.annual_withdrawals=0
    self.annual_capital_gains=0
    self.annual_gain=0
    self.share_price=1
    self.shares = self.amount/self.share_price
    self.activity = []

  def annual(self, year, birthyear) -> Mapping[str,Any]:
    self.annual_purchases=0
    self.annual_withdrawals = 0
    self.annual_capital_gains = 0
    self.annual_gain = self.amount * self.asset_class.annual_return
    if self.asset_class.fixed_income:
      self.shares += self.annual_gain/self.share_price
    else:
      self.share_price += self.share_price * self.asset_class.annual_return
    self.amount = self.shares * self.share_price
    remainder = self.annual_gain
    if self.reinv_asset:
      for a,f in self.reinv_asset:
        a_buy = self.annual_gain * f
        if a != self:
          self.sell(year, a_buy)
        a.buy(year, a_buy)
        remainder -= a_buy
    assert(remainder>=0)
    self._required_minimum_distribution(year, birthyear)
    taxable_withdrawals, taxable_capital_gains = self._annual_taxable_withdrawals()
    return dict(year=year, name=self.name, 
                amount=self.amount, 
                gain=self.annual_gain,
                purchases=self.annual_purchases,
                withdrawals=self.annual_withdrawals,
                capital_gains=self.annual_capital_gains,
                taxable_withdrawals=taxable_withdrawals, 
                taxable_capital_gains=taxable_capital_gains)
  
  def _required_minimum_distribution(self, year, birthyear):
    if self.investment_type.tax_deferred:
          rmd_amount = rmd_uniform_lifetime(self.amount, year-birthyear)
          rmd_amount -= self.annual_withdrawals
          if rmd_amount > 0:
            assert self.savings_asset, "Savings asset must be specified for assets incurring non-zero RMD"
            self.sell(year, rmd_amount)
            self.savings_asset.buy(year, rmd_amount)
 
  def _annual_taxable_withdrawals(self) -> Tuple[float,float]:
    taxable_withdrawals = self.annual_withdrawals if self.investment_type.tax_deferred else 0
    taxable_capital_gains = 0
    if not self.investment_type.tax_deferred and not self.investment_type.tax_free:
      taxable_capital_gains = self.annual_capital_gains
    return taxable_withdrawals, taxable_capital_gains

  def buy(self, year:int, deposit_amount:float) ->  None:
    self.annual_purchases += deposit_amount
    self.cost += deposit_amount
    self.shares += deposit_amount/self.share_price
    self.amount += deposit_amount

  def sell(self, year:int, expense_amount) -> float:
    withdrawal_amount = min(expense_amount, self.amount)
    deficit = expense_amount - withdrawal_amount
    self.amount -= withdrawal_amount
    shares_withdrawn = withdrawal_amount/self.share_price
    cost_of_shares_withdrawn = shares_withdrawn * self.cost/self.shares
    self.shares -= shares_withdrawn
    self.annual_withdrawals += withdrawal_amount
    self.annual_capital_gains += withdrawal_amount - cost_of_shares_withdrawn
    return max(deficit,0)
