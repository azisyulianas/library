from odoo import fields, models, api

class BookModel(models.Model):
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