# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from collections import OrderedDict
from odoo.http import request


class PortalInsurance(CustomerPortal):

    def _get_requests_searchbar_sortings(self):
        return {
            'date': {'label': _('Date'), 'order': 'create_date desc'},
            'duedate': {'label': _('Expiration Date'), 'order': 'insurance_expiration_date desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }

    def _get_requests_searchbar_filters(self):
        return {
            'all': {'label': _('All'), 'domain': []},
            'paid': {'label': _('Paid'), 'domain': [('state', '=', 'paid')]},
            'refused': {'label': _('Refused'), 'domain': [('state', '=', 'refused')]},
            'approved': {'label': _('Approved'), 'domain': [('state', '=', 'approved')]},
            'waiting': {'label': _('Waiting'), 'domain': [('state', '=', 'waiting')]},
            'expired': {'label': _('Expired'), 'domain': [('state', '=', 'expired')]},
        }

    def _prepare_my_insurance_requests_values(self, page, date_begin, date_end, sortby, filterby, domain=None, url="/my/insurance_requests"):
        values = self._prepare_portal_layout_values()
        insuranceRequest = request.env['insurance.request']
        domain = [('request_owner_id', '=', request.env.user.id)]
        searchbar_sortings = self._get_requests_searchbar_sortings()
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = self._get_requests_searchbar_filters()
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        values.update({
            'date': date_begin,
            # content according to pager and archive selected
            'requests': lambda pager_offset: insuranceRequest.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager_offset),
            'page_name': 'insurance_requests',
            'pager': {  # vals to define the pager.
                "url": url,
                "url_args": {'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
                "total": insuranceRequest.search_count(domain),
                "page": page,
                "step": self._items_per_page,
            },
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return values

    @http.route(['/my/insurance_requests', '/my/insurance_requests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_requests(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_my_insurance_requests_values(page, date_begin, date_end, sortby, filterby)

        # pager
        pager = portal_pager(**values['pager'])

        # content according to pager and archive selected
        requests = values['requests'](pager['offset'])
        request.session['my_requests_history'] = requests.ids[:100]

        values.update({
            'requests': requests,
            'pager': pager,
        })
        return request.render("NUSS_Students_Insurance.portal_my_insurance_requests", values)

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        values.update({
            'insurance_requests_count': request.env['insurance.request'].search_count([('request_owner_id', '=', request.env.user.id)])
        })
        return values