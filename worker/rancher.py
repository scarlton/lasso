import os
import datetime
import math
import plaid
from pymongo import MongoClient
# from coinbase.wallet.client import Client

from app import app

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')

plaidClient = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                  public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)

COINBASE_KEY = os.getenv('COINBASE_KEY')
COINBASE_SECRET = os.getenv('COINBASE_SECRET')
# coinbaseClient = Client(COINBASE_KEY, COINBASE_SECRET)

mongoClient = MongoClient('mongo', 27017)
db = mongoClient.lasso

@app.task(bind=True, default_retry_delay=10)
def lasso_transactions(self):
    txns = db.transactions.find({"lassoed": False})

    cumulative_roundup = 0
    txn_ids = []
    for tx in txns:
        cumulative_roundup += tx['roundup']
        txn_ids.append(tx['_id'])

    cumulative_roundup = round(cumulative_roundup, 2)
    if cumulative_roundup < 5:
        return '{} transactions for ${} left out to pasture'.format(len(txn_ids), cumulative_roundup)

    db.lassoes.insert({
        "amount": cumulative_roundup,
        "transactions": txn_ids,
        "captured": False
    })

    db.transactions.update_many({
        '_id' : {'$in' : txn_ids}
    }, {
        '$set': {'lassoed': True}
    })

    return 'lassoed {} transactions for ${}'.format(len(txn_ids), cumulative_roundup)


@app.task(bind=True, default_retry_delay=10)
def capture_funds(self, lasso_id):
    lasso = db.lassoes.find_one(lasso_id)

    if not lasso:
        return 'lasso {} does not exist'.format(lasso_id)

    if lasso['captured']:
        return 'lasso {} has already been captured'.format(lasso_id)

    try:
        # TODO: need a "funding account" associated with a user from which to pull the deposit
        balance_resp = plaidClient.Accounts.balance.get(access_token, account_ids=['ACCOUNT_ID'])
    except plaid.errors.PlaidError as e:
        raise self.retry(exc=e)

    available_balance = balance_resp['accounts'][0]['balances']['available']
    if available_balance <= lasso['amount']:
        return '{} is not enough to fund ${} for lasso {}'.format(available_balance, lasso['amount'], lasso_id)

    # TODO: coinbase depend on the deprecated pycrypto
    # coinbase_account = coinbaseClient.get_primary_account()
    # coinbase_account.deposit(amount=lasso['amount'], currency='USD')

    db.lassoes.update_one(lasso_id, {
        '$set': {'captured': True}
    })

    return 'deposited ${} for lasso {}'.format(lasso['amount'], lasso_id)
