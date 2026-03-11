def rebalance_portfolio(weights, threshold=0.05):
    return weights.apply(lambda x: max(x, threshold))
