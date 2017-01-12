from .. import app
from datetime import datetime


@app.template_filter()
def is_valid(voucher):
    """Check whether voucher is still valid"""

    valid = False
    if voucher:
        now = datetime.now()
        expires = datetime.strptime(
            voucher.get('expires'),
            "%Y-%m-%d %H:%M:%S.%f"
        )
        valid = now < expires

    return valid