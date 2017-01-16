from .. import app
from datetime import datetime


@app.template_filter()
def is_valid(voucher):
    """Check whether voucher is still valid"""

    valid = False
    if voucher:

        if "expires" in voucher:
            now = datetime.now()
            expires = datetime.strptime(
                voucher.get('expires'),
                "%Y-%m-%d %H:%M:%S.%f"
            )
            valid = now < expires

        if "count" in voucher and int(voucher.get("count")) > 0:
            valid = int(voucher.get("count")) > 0

    return valid
