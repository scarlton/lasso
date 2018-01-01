from collector import collect_transactions

if __name__ == '__main__':
    # TODO: programmatically loop through user's accounts
    #       to individually schedule task collection
    access_token = ''

    result = collect_transactions.delay(access_token)
    print('Task result:', result.result)
