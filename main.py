# In the (gacha) game Genshin Impact, players can buy a premium currency 
# (primogems) for in-game characters, items, etc. The premium currency 
# can be purchased in different amounts for different prices (in USD). 
# This script determines the optimal allocation which maximizes the amount
# of premium currency bought given some initial capital (in USD). 
# There is a promotional "first-time" bonus for each amount of premium
# currency, applied the first time it is bought.

# By changing the prices and values in the ***vals*** dictionary
# (and ***ft_vals*** if necessary), this script can be used to determine
# optimal allocation of funds for other games with premium currencies,
# using the first-time bonus dictionary and function if first-time bonuses
# exist in the other games.

# imports
import matplotlib.pyplot as plt
import pulp

# USD
st = 5
end = 2000
increment = 5
amounts_usd = list(range(st, end, increment))

# {USD amount: primogem amount}
vals = {
  1: 60,
  5: 330,
  15: 1090,
  30: 2240,
  50: 3880,
  100: 8080}

# first-time bonus applied
ft_vals = {
  1: 120,
  5: 600,
  15: 1960,
  30: 3960,
  50: 6560,
  100: 12960}

# no first time bonus applied
def opt_no_ft(amount):
  # define problem
  cost = pulp.LpProblem("primogems", pulp.LpMaximize)
  # initialize variables
  buy = pulp.LpVariable.dicts("Buy", vals.keys(), lowBound=0, cat="Integer")

  # objective
  cost += pulp.lpSum(buy[k] * vals[k] for k in vals.keys())
  # constraints
  cost += pulp.lpSum(buy[k] * k for k in vals.keys()) <= amount
  cost += pulp.lpSum(buy[k] for k in vals.keys()) >= 0
  # solve
  cost.solve()

  # get purchase quantities
  alloc = {int(str(v.name)[4:]): int(v.varValue) for v in cost.variables()}
  # sort keys so they are in ascending order
  alloc = {k: alloc[k] for k in sorted(alloc)}
  # get total amount of premium currency
  primogems = sum(alloc[k] * vals[k] for k in vals.keys())

  return (primogems, alloc)

# first-time bonus included
def opt_ft(amount):
  # define problem
  cost = pulp.LpProblem("primogems", pulp.LpMaximize)
  # initialize variables
  buy = pulp.LpVariable.dicts("Buy", vals.keys(), lowBound=0, cat="Integer")
  ft_buy = pulp.LpVariable.dicts("F-T", ft_vals.keys(), lowBound=0, \
    upBound=1, cat="Integer")

  # objective
  cost += (pulp.lpSum((buy[k] * vals[k]) + (ft_buy[k] * ft_vals[k]) \
    for k in vals.keys()))
  # constraints
  cost += \
    pulp.lpSum((buy[k] * k) + (ft_buy[k] * k) for k in vals.keys())  <= amount
  cost += pulp.lpSum(buy[k] for k in vals.keys()) >= 0
  for k in vals.keys():  cost += ft_buy[k] >= 0
  for k in vals.keys():  cost += ft_buy[k] <= 1

  # solve
  cost.solve()

  alloc = {k: 0 for k in vals.keys()}
  # get purchase quantities
  for v in cost.variables():
    for k in vals.keys():
      if v.name == f"Buy_{k}" or v.name == f"F_T_{k}":
        alloc[k] += int(v.varValue)

  # get total amount of premium currency
  primogems = 0
  for k in vals.keys():
    if alloc[k] > 0:  primogems += ft_vals[k]
    if alloc[k] > 1:  primogems += vals[k] * (alloc[k] - 1)

  return (primogems, alloc)

def opt(amount, first_time=False):
  if first_time:  return opt_ft(amount)
  if not first_time:  return opt_no_ft(amount)

# no first-time bonus applied
primogems_no_ft = {amt: opt(amt, False)[0] for amt in amounts_usd}
primogems_per_usd_no_ft = {k: round(v / k, 3) for k, v in primogems_no_ft.items()}

# first-time bonus included
primogems_ft = {amt: opt(amt, True)[0] for amt in amounts_usd}
primogems_per_usd_ft = {k: round(v / k, 3) for k, v in primogems_ft.items()}

print(primogems_per_usd_no_ft)
print(primogems_per_usd_ft)

plt.plot(primogems_per_usd_no_ft.keys(), primogems_per_usd_no_ft.values())
plt.title("No First Time Bonus applied")
plt.show()
plt.plot(primogems_per_usd_ft.keys(), primogems_per_usd_ft.values())
plt.title("First Time Bonus included")
plt.show()


