from odoo import fields, models, api
from odoo.exceptions import ValidationError

class BookModel(models.Model):
    '''
    Describes a Book catalogue.
    '''

    _name = "library.book"
    _description = "Book"

    # tambahan dari ch06:
    _order = "name, date_published desc"
    _rec_name = "name"
    _table = "library_book"
    _log_access = True
    _auto = True

    #string
    name = fields.Char(
        "Title",
        default=None,
        help="Book cover title.",
        readonly=False,
        required=True,
        index=True,
        copy=False,
        groups="",
        states={},
        )
    is_available = fields.Boolean('Is Available?')
    isbn = fields.Char(help="Use a Valid ISBN-13 or ISBN-10")
    publisher_id = fields.Many2one(index=True)
    book_type = fields.Selection([
        ("paper","Paperback"),
        ("hard","Hardcover"),
        ("electronic","Electronic"),
        ("other","Other"),
    ], "Type")
    notes = fields.Text("Internal Notes")
    descr = fields.Html("Description")

    # Numeric fields
    copies = fields.Integer(default=1)
    avg_rating =fields.Float("Average Rating", (3, 2))
    price = fields.Monetary("Price", "currency_id")

    # price helper
    currency_id = fields.Many2one('res.currency')

    # Date and time fields
    date_published = fields.Date()
    last_borrow_date = fields.Datetime(
        "Last Borrowed On",
        default=lambda self: fields.Datetime.now()
    )

    # Other fields
    active = fields.Boolean("Active?", default=True)
    image = fields.Binary("Cover")

    # Relational Fields
    publisher_id = fields.Many2one("res.partner", string="Publisher")
    # author_ids = fields.Many2many(
    #     "res.partner", 
    #     string="Authors"
    # )

    # Relational Fields Change Name
    # Book <-> Authors relation (using positional args)
    author_ids = fields.Many2many(
        'res.partner',
        'library_book_res_partner_rel',
        'a_id',
        'b_id',
        'Author'
    )
    # OR
    # author_ids = fields.Many2many(
    #     comodel_name='res.partner',
    #     relation='library_book_res_partner_rel',
    #     column1='a_id',
    #     column2='b_id',
    #     string='Author'
    # )

    publisher_country_id = fields.Many2one(
        'res.country', string='Publisher Country',
        compute='_compute_publisher_country',
        inverse='_inverse_publisher_country',
        search='_search_publihser_country',
        # related='publisher_id.country_id',
    )

    _sql_constraints = [
        ('library_book_name_date_uq',
        'UNIQUE (name, date_published)',
        'Title and publication date must be unique'),
        ('library_book_check_date',
        'CHECK (date_published <= current_date)',
        'Publication date must not be in the future')
    ]

    @api.depends("publisher_id.country_id")
    def _compute_publisher_country(self):
        for book in self:
            book.publisher_country_id = book.publisher_id.country_id

    def _inverse_publisher_country(self):
        for book in self:
            book.publisher_id.country_id = book.publisher_country_id

    def _search_publihser_country(self, operator, value):
        return [("publisher_id.country_id", operator, value)]

    @api.constrains('avg_rating')
    def _constrain_avg_rating_valid(self):
        for book in self:
            if book.avg_rating >10 or book.avg_rating<0:
                raise ValidationError(
                    f'{book.avg_rating} is an invalid average rating'
                )

    @api.constrains('isbn')
    def _constrain_isbn_valid(self):
        for book in self:
            if book.isbn and not book._check_isbn():
                raise ValidationError(
                    f'{book.isbn} is an invalid ISBN'
                )

    def _check_isbn(self):
        self.ensure_one()
        digits = [int(x) for x in self.isbn if x.isdigit()]
        if len(digits) == 13:
            ponderations = [1, 3] * 6
            terms = [a * b for a, b in zip(digits[:12], ponderations)]
            remain = sum(terms) % 10
            check = 10 - remain if remain != 0 else 0
            return digits[-1] == check
        if len(digits) == 10:
            ponderators = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            total = sum(
                a*b for a,b in zip(digits[:9], ponderators)
            )
            check = total % 11
            return digits[-1]==check

    def button_check_isbn(self):
        for book in self:
            if not book.isbn:
                raise ValidationError("Please provide an ISBN for %s" % book.name)
            if book.isbn and not book._check_isbn():
                raise ValidationError("%s ISBN is invalid" %book.isbn)
        return True

class BookModelExtended(models.Model):
  _inherit = 'library.book'
  cost = fields.Float(string="Cost")
  is_published = fields.Boolean(string='Already Published to Inventory', default=False)
  product_id = fields.Many2one('product.product', string="Product View", readonly=True)
  purchase_count= fields.Float(string="Purchase Book",
    compute='_compute_book_purchase',
    default=0
  )
  sale_count = fields.Float(string="Sold Book",
    compute='_compute_book_sales',
    default=0
  )
  stock = fields.Float(string="Stock", related='product_id.qty_available', store=True, readonly=True)

  def _compute_book_sales(self):
    count = self.env['sale.order'].search_count([('order_line.product_id', '=', self.product_id.id)])
    for book in self:
      book.sale_count = count
  
  def _compute_book_purchase(self):
    count = self.env['purchase.order'].search_count([('product_id', '=', self.product_id.id)])
    for book in self:
      book.purchase_count = count

  def action_publish_to_inventory(self):
    for book in self:
      if not book.product_id:
        product = self.env['product.product'].create({
          'name': self.name,
          'type': 'product',
          'standard_price': book.cost,
          'default_code': book.isbn,
          'description': f'{book.descr}',
          'list_price':book.cost,
          'lst_price':book.cost,
          "standard_price":book.price,
          'image_1920':book.image,
        })
        
        book.product_id = product.id
        book.is_published = True

  def action_sell(self):
    self.ensure_one()
    action = {
      'type': 'ir.actions.act_window',
      'name': 'Sales Order',
      'res_model': 'sale.order',
      'view_mode': 'form',
      'target': 'current',
      'res_id': False,
      'context': {
        'default_sale_order_template_id':"",            
        'default_order_line': [
          (0, 0, {
            'product_id': self.product_id.id,
            'product_template_id': self.product_id.product_tmpl_id.id,
            'name': self.product_id.name,
            'product_uom_qty': 2,
            'product_uom': self.product_id.uom_po_id.id,
            'price_unit': self.product_id.list_price,
          })
        ],
      },
    }

    return action

  def action_purchase(self):
    ayam = self.product_id
    self.ensure_one()
    action = {
      'type': 'ir.actions.act_window',
      'name': 'Purchase Order',
      'res_model': 'purchase.order',
      'view_mode': 'form',
      'target': 'current',
      'context': {
        'default_order_line': [(0, 0, {
          'product_id': self.product_id.id,
          'name': self.product_id.name,
          'product_qty': 1,
          'product_uom': self.product_id.uom_po_id.id,
          'price_unit': self.product_id.standard_price,
          "price_subtotal": self.product_id.list_price,
        })],
      },
    }

    return action

  def purchase_book_list(self):
    self.ensure_one()
    Purchase = self.env['purchase.order'].search([('product_id','=',self.product_id.id)])
    action = {
      'name': 'Purchase',
      'type': 'ir.actions.act_window',
      'res_model': 'purchase.order',
      'context': {'create': False},
    }
    lenght = len(Purchase)
    if len(Purchase) == 1:
        action.update({
            'view_mode': 'form',
            'res_id': Purchase.id,
        })
    else:
        action.update({
            'view_mode': 'tree,form',
            'domain': [('product_id','=',self.product_id.id)],
        })

    return action

  def sales_book_list(self):
    self.ensure_one()
    Sales = self.env['sale.order'].search([('order_line.product_id','=',self.product_id.id)])
    action = {
      'name': 'Sales',
      'type': 'ir.actions.act_window',
      'res_model': 'sale.order',
      'context': {'create': False},
    }
    if len(Sales) == 1:
        action.update({
            'view_mode': 'form',
            'res_id': Sales.id,
        })
    else:
        action.update({
            'view_mode': 'tree,form',
            'domain': [('order_line.product_id','=',self.product_id.id)],
        })

    return action