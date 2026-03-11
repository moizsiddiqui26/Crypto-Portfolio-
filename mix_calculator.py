import pandas as pd

def calculate_mix(data, amount, level):

    returns = data.pct_change().dropna()
    avg_return = returns.mean()
    risk = returns.std()

    weights = avg_return / risk

    if level == "Low Risk":
        weights = weights / weights.sum()

    elif level == "Medium Risk":
        weights = (weights * 1.2) / (weights * 1.2).sum()

    else:
        weights = (weights * 1.5) / (weights * 1.5).sum()

    allocation = weights * amount

    return weights, allocation
