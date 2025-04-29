{
    "name": "Library Management",
    "summary": "Manage library catalog and book lending.",
    "author": "Daniel Reis",
    "license": "AGPL-3",
    "website": "https://github.com/PacktPublishing"
               "/Odoo-15-Development-Essentials",
    "version": "0.11",
    "category": "Services/Library",
    "depends": ["base","mail"],
    "data": [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        "views/book_view.xml",
        "views/library_menu.xml",
        "views/book_list_template.xml",
        "views/member_view.xml",
        "reports/library_book_report.xml",
        "reports/library_publisher_report.xml",
        ],
    "application": True,
    "demo":[
        'demo/res.partner.csv',
        'demo/library.book.csv',
        'demo/book_demo.xml',
        # 'demo/library.member.csv'
    ]
}