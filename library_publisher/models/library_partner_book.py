from odoo import fields, models
class Partner(models.Model):
    _inherit = 'res.partner'
    published_book_ids = fields.One2many(
        'library.book',
        'publisher_id',
        string="Published Books"
    )

    book_count = fields.Integer(string="Publihsed Book",
        compute='_compute_book_publihsed',
        default=0
    )

    def _compute_book_publihsed(self):
        for partner in self:
            partner.book_count = self.env['library.book'].search_count(
                [('publisher_id', '=', self.id)])


    def published_book_list(self):
        self.ensure_one()
        
        action = {
            'name': 'Book',
            'type': 'ir.actions.act_window',
            'res_model': 'library.book',
            'context': {'create': False},
        }
        
        if len(self.published_book_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.published_book_ids.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('publisher_id', '=', self.id)],
            })

        return action