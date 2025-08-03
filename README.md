# Django E-Commerce Platform

A robust and scalable eCommerce web application built with Django. This project offers a seamless online shopping experience including product browsing, wishlist management, shopping cart, checkout, user authentication, and payment processing with SSLCommerz.

---

## Features

- **User Authentication**: Registration, login, logout, and profile management with editable user information.
- **Product Catalog**: Browse products with search functionality.
- **Wishlist**: Add/remove products to a personalized wishlist.
- **Shopping Cart**: Add, update, or remove products from the cart.
- **Checkout Process**: Order review and shipping information input.
- **Order Management**: View past completed orders in user profile.
- **Payment Integration**: Secure payment gateway using SSLCommerz sandbox API.
- **Guest Checkout**: Support for users without accounts to place orders.
- **Responsive UI**: Clean and user-friendly interface.

---

## Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
SSLCOMMERZ_STORE_ID = 'your_store_id'
SSLCOMMERZ_STORE_PASSWORD = 'your_store_password'
python manage.py runserver
├── accounts/           # Django app for user & eCommerce logic
│   ├── templates/      # HTML templates for UI
│   ├── models.py       # Data models (User, Product, Wishlist, Order, etc.)
│   ├── views.py        # Views and business logic
│   ├── forms.py        # Forms for registration and profile editing
│   ├── utils.py        # Helper functions (cart handling, guest order, etc.)
├── manage.py
├── requirements.txt
└── README.md
Technologies Used
Python 3.x

Django 3.x or 4.x

SQLite (default) or any other Django-supported database

HTML, CSS (can be extended with Tailwind, Bootstrap, etc.)

Requests library for SSLCommerz integration

Contributing
Feel free to submit issues or pull requests to improve the project. For major changes, please open an issue first to discuss what you would like to change.

License
This project is open source and available under the MIT License.
