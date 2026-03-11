from concurrent.futures import ThreadPoolExecutor

def risk_checker(df):
    return df.pct_change().std()

def predictor(df):
    return df.pct_change().mean()

def parallel_risk_prediction(data):

    with ThreadPoolExecutor() as executor:
        risk_future = executor.submit(risk_checker, data)
        pred_future = executor.submit(predictor, data)

    return risk_future.result(), pred_future.result()
