
from dataclasses import dataclass
'''
Using Uniform Lifetime Table from https://www.irs.gov/publications/p590b#en_US_2023_publink100090310
Table III
(Uniform Lifetime)
For Use by:
Unmarried Owners,
Married Owners Whose Spouses Aren't More Than 10 Years Younger, and
Married Owners Whose Spouses Aren't the Sole Beneficiaries of Their IRAs)
'''

UL_START_AGE=72
UL_DISTB_PERIOD=[27.4, 26.5, 25.5, 24.6, 23.7, 22.9, 22.0, 21.1, 20.2, 19.4, 18.5, 17.7, 16.8, 16.0, 15.2, 14.4, 13.7, 12.9, 12.2, 11.5, 10.8, 10.1, 9.5, 8.9, 8.4, 7.8, 7.3, 6.8, 6.4, 6.0, 5.6, 5.2, 4.9, 4.6, 4.3, 4.1, 3.9, 3.7, 3.5, 3.4, 3.3, 3.1, 3.0, 2.9, 2.8, 2.7, 2.5, 2.3, 2.0]
MIN_AGE=75

def rmd_uniform_lifetime(asset_amount:float, owner_age:int) -> float:
  if owner_age < MIN_AGE:
    return 0
  else:
    return asset_amount/UL_DISTB_PERIOD[owner_age-UL_START_AGE]