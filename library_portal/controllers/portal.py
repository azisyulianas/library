from odoo.http import route, request
from odoo.addons.portal.controllers import portal
class CustomerPortal(portal.CustomerPortal):
  def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "book_checkout_count" in counters:
            count = request.env["library.checkout"].search_count([])
            values["book_checkout_count"] = count
        return values
  
  @route(
      ["/my/book-checkouts", "/my/book-checkouts/page/<int:page>"],
      auth="user",
      website=True,
  )
  def my_book_checkouts(self, page=1, **kw):
      Checkout = request.env["library.checkout"]
      domain = []
      # Prepare pager data
      checout_count = Checkout.search_count(domain)
      pager_data = portal.pager(
        url="/my/book_checkouts",
        total=checout_count,
        page=page,
        step=self._items_per_page
      )

      # Recodset according to pager and domain filter
      checouts = Checkout.search(
        domain=domain,
        limit=self._items_per_page,
        offset=pager_data['offset']
      )
      values = self._prepare_portal_layout_values()
      values.update(
        {
          "checkouts":checouts,
          "page_name":"book-checkouts",
          "default_url":"/my/book-checkouts",
          "pager":pager_data,
        }
      )
      return request.render(
        'library_portal.my_book_checkouts',
        values
      )

  @route(
    ["/my/book-checkout/<model('library.checkout'):doc>"],
    auth='user',
    website=True
  )
  def portal_my_project(self, doc=None, **kw):
    return request.render(
      "library_portal.book_checkout",
      {"doc":doc}
    )