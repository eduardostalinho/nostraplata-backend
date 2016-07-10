import time
from decimal import Decimal
from flask import Flask, jsonify, request
from redis import StrictRedis

app = Flask(__name__)
store = StrictRedis()

@app.route('/transaction/', methods=['GET', 'POST'])
def create_transaction():
    if request.method == 'POST':
        creditor = request.form['creditor']
        debtor = request.form['debtor']
        paying = request.form.get('paying')

        if paying:
            t_type = 'paid'
        else:
            t_type = 'loan'

        timestamp = time.time()

        key = '{}:{}:{}:{}'.format(timestamp, creditor, debtor, t_type)
        value = request.form['value']

        store.set(key , value)

        response = {'data': {key: value}}

        return jsonify(response), 201

    if request.method == 'GET':
        user = request.form['user']

        debts = store.keys('*:*:{}:*'.format(user))
        credits = store.keys('*:{}:*:*'.format(user))
        debt = [ (t.decode('utf-8'), float(store.get(t))) for t in debts ]
        credit = [ (t.decode('utf-8'), float(store.get(t))) for t in credits ]
        balance = sum(x[1] for x in credit) - sum(x[1] for x in debt)

        data = {'data': {
            'debt_transactions': debt,
            'credit_transactions': credit,
            'balance': balance,
        }}

        return jsonify(data)
