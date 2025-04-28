# -*- coding: utf-8 -*-
from odoo import http

class Books(http.Controller):
    @http.route("/library/books")
    def list(self, **kwargs):
        Book = http.request.env["library.book"]
        books = Book.search([])
        return http.request.render(
            "library_app.book_list_template",
            {"books": books}
        )

    @http.route("/api/library/books", auth='public')
    def getJsonData(self, **kwargs):
        Book = http.request.env["library.book"]
        book = Book.search_read([],['name', 'id', 'author_ids', 'publisher_id'])
        return http.request.make_json_response(
            data={'nama':'Azis Yulianas', 'book':book, 'ayam':True},
            status=200,
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

