from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple
import numpy as np

@dataclass
class InvestmentType:
  name:str
  tax_deferred:bool # pay tax on withdrawal as ordinary income
  tax_free:bool # no tax on dividends and capital gain (roth)

INV_BROKERAGE = InvestmentType('brokerage', False, False)
INV_401K = InvestmentType('brokerage', True, False)
INV_ROTH = InvestmentType('brokerage', False, True)

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
  reinv_asset:List[Tuple['Asset',float]]=field(default_factory=list)
  annual_withdrawals=0
  annual_capital_gains=0
  share_price=1

  def __post_init__(self):
        self.shares = self.amount/self.share_price

  def set_reinv_asset(self, asset:'Asset', fraction:float) -> None:
    self.reinv_asset.append((asset, fraction))

  def annual(self) -> Tuple[float,float]:
    self.annual_withdrawals = 0
    self.annual_capital_gains = 0
    gain = self.amount * self.asset_class.annual_return
    if self.asset_class.fixed_income:
      self.shares += gain/self.share_price
    else:
      self.share_price += self.share_price * self.asset_class.annual_return
    self.amount = self.shares * self.share_price
    remainder = gain
    if self.reinv_asset:
      for a,f in self.reinv_asset:
        a_buy = gain * f
        if a != self:
          self.sell(a_buy)
        a.buy(a_buy)
        remainder -= a_buy
    assert(remainder>=0)
    return self._annual_taxable_withdrawals()

  def _annual_taxable_withdrawals(self) -> Tuple[float,float]:
    taxable_withdrawals = self.annual_withdrawals if self.investment_type.tax_deferred else 0
    taxable_capital_gains = 0
    if not self.investment_type.tax_deferred and not self.investment_type.tax_free:
      taxable_capital_gains = self.annual_capital_gains
    self.annual_withdrawals = 0
    self.annual_capital_gains = 0
    return taxable_withdrawals, taxable_capital_gains

  def buy(self, deposit_amount:float) ->  None:
    self.cost += deposit_amount
    self.shares += deposit_amount/self.share_price
    self.amount += deposit_amount

  def sell(self, expense_amount) -> float:
    withdrawal_amount = min(expense_amount, self.amount)
    deficit = expense_amount - withdrawal_amount
    self.amount -= withdrawal_amount
    shares_withdrawn = withdrawal_amount/self.share_price
    cost_of_shares_withdrawn = shares_withdrawn * self.cost/self.shares
    self.shares -= shares_withdrawn
    self.annual_withdrawals += withdrawal_amount
    self.annual_capital_gains += withdrawal_amount - cost_of_shares_withdrawn
    return max(deficit,0)
