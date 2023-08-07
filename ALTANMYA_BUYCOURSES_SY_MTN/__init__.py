from . import controllers
from . import models

from odoo.addons.payment import setup_provider, reset_payment_provider


def post_init_hook(cr, registry):
    print('6565656')
    setup_provider(cr, registry, 'syriatell12')


def uninstall_hook(cr, registry):
    print('6565656')
    reset_payment_provider(cr, registry, 'syriatell12')
