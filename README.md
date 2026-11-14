# FationLink

A clothing marketplace built with Django. Customers buy clothes from sellers, and sellers connect with wholesalers and manufacturers. The project also includes machine-learning experiments on reviews, fraud and demand.

## Features

- Custom user model with four roles: customer, seller, wholesaler, manufacturer
- Registration, login and logout
- Product catalog with category filter and product detail pages
- Session-based shopping cart and checkout (stock is reduced inside a database transaction)
- Order history for customers
- Seller panel: add, edit and delete products, and manage sales and order status
- Product reviews and ratings (only buyers can review)
- Suppliers page for connecting sellers with wholesalers and manufacturers
- Responsive UI with Bootstrap 5

## Tech stack

- Python, Django
- SQLite (development)
- Bootstrap 5 (CDN)
- scikit-learn / joblib for the ML parts

## Getting started

```bash
git clone <your-repo-url>
cd FationLink
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ for the shop and http://127.0.0.1:8000/admin/ for the admin panel.

## Roles

| Role | What they can do |
|---|---|
| Customer | Browse, add to cart, order, review purchased products |
| Seller | Everything a customer can, plus manage own products and sales |
| Wholesaler / Manufacturer | Seller features, listed as suppliers |

## Project structure

```
FationLink/
  accounts/   custom user model, registration and login
  shop/       products, cart, orders, reviews, seller panel
  config/     Django settings and root URLs
  ml/         model training scripts (reviews)
  data/       datasets used by the ML scripts
  manage.py
```

## Machine learning

- `ml/yelp_train.py` trains a text model on review data; the vectorizer is saved as `yelp_vectorizer.joblib`
- `shop/fraud.py`, `shop/demand.py` and `shop/sentiment.py` contain the fraud-detection, demand-forecasting and review-sentiment logic
- `download_*.py` scripts in the project root download the datasets for demand, fraud, retail and reviews

## Notes

- `DEBUG = True` and the default `SECRET_KEY` are for development only. Change both before deploying.
- `db.sqlite3` is not tracked in git.

## Roadmap

- Separate order status per product
- Payment gateway integration
- Product images
- Deployment settings
