from dataclasses import dataclass
from typing import Iterable, Optional, Tuple
import numpy as np

@dataclass
class InvestmentType:
  name:str
  tax_deferred:bool
  pre_tax:bool
  rmd_needed: bool

@dataclass
class AssetClass:
  name:str
  annual_return:float

@dataclass
class Asset:
  name:str
  amount:float
  investment_type:InvestmentType
  asset_class:AssetClass
  reinv_asset=None

  def set_reinv_asset(self, asset:'Asset', fraction:float):
    if not self.reinv_asset:
      self.reinv_asset = list()
    self.reinv_asset.append((asset, fraction))

  def annual(self):
    ret = self.amount * self.asset_class.annual_return
    remainder = ret
    if self.reinv_asset:
      for a,f in self.reinv_asset:
        aret = ret * f
        a.amount += aret
        remainder -= aret
    self.amount += remainder