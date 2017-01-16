import time
from datetime import datetime, timedelta

import Mollie
import redis
from flask import json
from flask import request, redirect, \
    render_template, make_response, jsonify, Response
from werkzeug.datastructures import Headers

from . import app
from utils import filters

mollie = Mollie.API.Client()
mollie.setApiKey(app.config.get('MOLLIE_API_KEY'))

VOUCHER_DB = redis.StrictRedis(app.config.get('REDIS_HOST'))
PAYWALL_VOUCHER_COOKIE = app.config.get('COOKIE_NAME')

# TODO make TTW configurable
VOUCHER_TYPES = {
    # expiration vouchers
    0: {'type': 1, 'amount': 2.50, 'description': '1 day access', 'days': 1},
    1: {'type': 1, 'amount': 4.50, 'description': '2 day access', 'days': 2},
    2: {'type': 1, 'amount': 6.50, 'description': '3 day access', 'days': 3},

    # nuber of visits vouchers
    10: {'type': 2, 'amount': 1.00, 'description': '100 visits', 'count': 100},
    20: {'type': 2, 'amount': 1.75, 'description': '200 visits', 'count': 200},
    30: {'type': 2, 'amount': 2.50, 'description': '300 visits', 'count': 300},
}

# Which voucher types are expirable
EXP_TYPES = [v for v in VOUCHER_TYPES.keys()
             if VOUCHER_TYPES[v].get('type') == 1]

# Which vouchers are limited by number of visits
NOV_TYPES = [v for v in VOUCHER_TYPES.keys()
             if VOUCHER_TYPES[v].get('type') == 2]


@app.route('/')
def enter_voucher():

    return render_template(
        'verify_voucher.html'
    )


@app.route('/new_voucher')
def new_voucher():

    return render_template(
        'new_voucher.html',
        exp_types=EXP_TYPES,
        nov_types=NOV_TYPES,
        voucher_types=VOUCHER_TYPES
    )


@app.route('/manage_vouchers')
def manage_vouchers():

    current_cookie = False
    if PAYWALL_VOUCHER_COOKIE in request.cookies:
        current_cookie = request.cookies.get(PAYWALL_VOUCHER_COOKIE)

    return render_template(
        'manage_vouchers.html',
        vouchers=VOUCHER_DB,
        current_cookie=current_cookie
    )


@app.route('/delete_voucher/<string:voucher_code>')
def delete_voucher(voucher_code):

    if voucher_code == 'all_expired':
        for vc in VOUCHER_DB.keys():
            if not filters.is_valid(VOUCHER_DB.hgetall(vc)):
                VOUCHER_DB.delete(vc)
    else:
        VOUCHER_DB.delete(voucher_code)

    return redirect('/manage_vouchers')


@app.route('/verify_voucher', methods=['POST'])
@app.route('/verify_voucher/<string:voucher_code>', methods=['GET'])
def verify_voucher(voucher_code=None):

    # check POST params
    if not voucher_code:
        voucher_code = request.form.get('voucher_code')

    voucher = VOUCHER_DB.hgetall(voucher_code)

    if voucher:

        valid = False
        resp_header = ""

        # expiration voucher
        if voucher.get('expires'):

            now = datetime.now()
            expires = datetime.strptime(
                voucher.get('expires'),
                "%Y-%m-%d %H:%M:%S.%f"
            )

            valid = now < expires
            minutes_remaining = str(
                (expires - now).
                total_seconds() / 60)

            resp_header = {'Minutes-Remaining': minutes_remaining}

        # number of visits voucher
        if voucher.get('count'):

            count = int(voucher.get('count'))
            valid = count > 0

            resp_header = {'Visits-Remaining': count - 1}

            voucher['count'] = count - 1
            VOUCHER_DB.hmset(voucher_code, voucher)

        # a valid and paid voucher
        if valid and voucher.get('status') == 'paid':

            resp = make_response(json.dumps(voucher))
            resp.headers = Headers(resp_header)
            resp.mimetype = 'application/json'
            resp.set_cookie(PAYWALL_VOUCHER_COOKIE, voucher_code)
            return resp

    # invalid or no voucher. Redirect to new voucher screen
    if request.is_xhr:
        data = {'redirect': '/new_voucher'}
        resp = make_response(json.dumps(data))
        resp.mimetype = 'application/json'
        return resp
    else:
        return redirect('/new_voucher')


@app.route('/webhook_verification/<string:voucher_code>',
           methods=['GET', 'POST'])
def webhook_verification(voucher_code):

    try:
        payment_id = VOUCHER_DB.hgetall(voucher_code).get('payment_id')
        payment = mollie.payments.get(payment_id)
        voucher_type = int(payment['metadata']['voucher_type'])

        voucher = {
            'payment_id': payment['id'],
            'status': payment['status']
        }

        # set expiration date
        if voucher_type in EXP_TYPES:
            voucher['expires'] = \
                datetime.now() + \
                timedelta(days=VOUCHER_TYPES[voucher_type].get('days'))

        # set number of visits
        if voucher_type in NOV_TYPES:
            voucher['count'] = VOUCHER_TYPES[voucher_type].get('count')

        VOUCHER_DB.hmset(voucher_code, voucher)

        if payment.isPaid():
            return 'Paid'
        elif payment.isPending():
            return 'Pending'
        elif payment.isOpen():
            return 'Open'
        else:
            return 'Cancelled'

    except Mollie.API.Error as e:
        return 'API call failed: ' + e.message


@app.route('/make_payment', methods=['POST'])
@app.route('/make_payment/<int:voucher_type>', methods=['POST', 'GET'])
def make_payment(voucher_type=None):

    # check POST params
    if not voucher_type:
        voucher_type = int(request.form.get('voucher_type'))

    # TODO consider re-charging an old voucher code
    voucher_code = str(int(time.time()))

    payment = mollie.payments.create({
        'amount': VOUCHER_TYPES[voucher_type].get('amount'),
        'description': VOUCHER_TYPES[voucher_type].get('description'),
        'webhookUrl':
            request.url_root +
            'webhook_verification/%s' % voucher_code,
        'redirectUrl': request.url_root + 'verify_voucher/' + voucher_code,
        'metadata': {
            'voucher_code': voucher_code,
            'voucher_type': voucher_type
        }
    })

    voucher = {
        'payment_id': payment.get('id'),
        'status': payment.get('status'),
    }

    if voucher_type in EXP_TYPES:
        voucher['expires'] = datetime.now()

    if voucher_type in NOV_TYPES:
        voucher['count'] = 0

    # create voucher entry in database
    VOUCHER_DB.hmset(voucher_code, voucher)

    return redirect(payment.getPaymentUrl())
