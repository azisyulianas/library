from odoo import http
from odoo.addons.library_app.controllers.main import Books

class BookExtended(Books):
    @http.route()
    def list(self, **kwargs):
        response = super().list(**kwargs)
        if kwargs.get('available'):
            all_book = response.qcontext['books']
            available_book = all_book.filtered(
                'is-available'
            )
            response.qcontext["books"] = available_book
        return response