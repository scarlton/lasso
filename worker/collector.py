import os
import datetime
import math
import plaid
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from app import app

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')

plaidClient = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                  public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)

mongoClient = MongoClient('mongo', 27017)
db = mongoClient.lasso

@app.task(bind=True, default_retry_delay=10)
def collect_transactions(self, ):
    # Pull transactions for the last 14 days
    start_date = "{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(-14))
    end_date = "{:%Y-%m-%d}".format(datetime.datetime.now())

    try:
        response = plaidClient.Transactions.get(ACCESS_TOKEN, start_date, end_date)
    except plaid.errors.PlaidError as e:
        raise self.retry(exc=e)

    collected_transactions = 0
    skipped_transactions = 0
    for tx in response['transactions']:
        if (tx['amount'] > 0 and not tx['pending']):
            roundup = round(math.ceil(tx['amount']) - tx['amount'], 2)
            if (roundup == 0):
                roundup = 1

            try:
                db.transactions.insert({
                    "_id": tx['transaction_id'],
                    "account_id": tx['account_id'],
                    "amount": tx['amount'],
                    "name": tx['name'],
                    "transacted_at": tx['date'],
                    "lassoed": False,
                    "roundup": roundup
                })
                collected_transactions += 1
            except DuplicateKeyError:
                skipped_transactions +=1
        else:
            skipped_transactions +=1

    return 'Collected {} transactions; skipped {}'.format(collected_transactions, skipped_transactions)
