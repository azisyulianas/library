# -*- coding: utf-8 -*-
from odoo import http

class Books(http.Controller):
    @http.route("/library/books")
    def list(self, **kwargs):
        Book = http.request.env["library.book"]
        books = Book.search([])
        if kwargs.get('available'):
            available_book = Book.search([('is_available','=',True)])
            return http.request.render(
                "library_app.book_list_template",
                {"books": available_book}
            )
        return http.request.render(
            "library_app.book_list_template",
            {"books": books}
        )
    @http.route('/library/catalog', auth='public', website=True)
    def catalog(self):
        Book = http.request.env['library.book']
        books = Book.sudo().search([])
        return http.request.render(
            'library_app.book_catalog',
            {'books':books},
        )
# class LibraryApp(http.Controller):
#     @http.route('/library_app/library_app', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/library_app/library_app/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('library_app.listing', {
#             'root': '/library_app/library_app',
#             'objects': http.request.env['library_app.library_app'].search([]),
#         })

#     @http.route('/library_app/library_app/objects/<model("library_app.library_app"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('library_app.object', {
#             'object': obj
#         })

