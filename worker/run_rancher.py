from investor import lasso_transactions

if __name__ == '__main__':
    # TODO: programmatically loop through user's accounts
    #       to individually lasso transactions

    result = lasso_transactions.delay()
    print('Task result:', result.result)
