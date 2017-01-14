import time
from datetime import datetime, timedelta

import Mollie
import redis
from flask import Response, request, redirect, \
    render_template

from . import app
from utils import filters

mollie = Mollie.API.Client()
mollie.setApiKey(app.config.get('MOLLIE_API_KEY'))

voucher_db = redis.StrictRedis('localhost')

PAYWALL_VOUCHER_COOKIE = 'Paywall-Voucher'


@app.errorhandler(401)
def custom_401(error):
    return Response(
        'PAY UP PANCAKE!',
        401,
        {'Minutes-Remaining': '0'})


@app.route('/')
def index():
    current_cookie = False
    if PAYWALL_VOUCHER_COOKIE in request.cookies:
        current_cookie = request.cookies.get(PAYWALL_VOUCHER_COOKIE)

    return render_template(
        'vouchers.html',
        vouchers=voucher_db,
        current_cookie=current_cookie
    )


@app.route('/delete_voucher/<string:voucher_code>')
def delete_voucher(voucher_code):
    if voucher_code == 'all_expired':
        for vc in voucher_db.keys():
            if not filters.is_valid(voucher_db.hgetall(vc)):
                voucher_db.delete(vc)
    else:
        voucher_db.delete(voucher_code)

    return redirect('/')


@app.route('/buy_voucher')
def buy_voucher():
    return make_payment()


@app.route('/verify_voucher/<string:voucher_code>')
def verify_voucher(voucher_code):
    voucher = voucher_db.hgetall(voucher_code)

    if voucher:
        now = datetime.now()
        expires = datetime.strptime(
            voucher.get('expires'),
            "%Y-%m-%d %H:%M:%S.%f"
        )

        if voucher.get('status') == 'paid' and \
                        now < expires:
            resp = Response(
                'VALID',
                200,
                {'Minutes-Remaining': str(
                    (expires - now).
                    total_seconds() / 60
                )}
            )

            resp.set_cookie(PAYWALL_VOUCHER_COOKIE, voucher_code)
            return resp

    # invalid or no voucher, redirect to payment provider
    return make_payment()


@app.route('/webhook_verification/<string:voucher_code>',
           methods=['GET', 'POST'])
def webhook_verification(voucher_code):
    try:
        payment_id = voucher_db.hgetall(voucher_code).get('payment_id')
        payment = mollie.payments.get(payment_id)
        voucher_code = payment['metadata']['voucher_code']

        voucher_db.hmset(voucher_code, {
            'payment_id': payment['id'],
            'expires': datetime.now() + timedelta(minutes=10),
            'status': payment['status']
        })

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


def make_payment():
    # TODO consider re-charging an old voucher code
    voucher_code = str(int(time.time()))

    payment = mollie.payments.create({
        'amount': 1.00,
        'description': 'Paywall Voucher',
        'webhookUrl': request.url_root + 'webhook_verification/' + voucher_code,
        'redirectUrl': request.url_root + 'verify_voucher/' + voucher_code,
        'metadata': {
            'voucher_code': voucher_code
        }
    })

    # create expired entry in database
    voucher_db.hmset(voucher_code, {
        'payment_id': payment.get('id'),
        'expires': datetime.now(),
        'status': payment.get('status')
    })

    return redirect(payment.getPaymentUrl())
