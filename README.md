# GlowMore Beauty & Cosmetics Store

GlowMore is a premium beauty and cosmetics e-commerce store built with Django.

## Features
- **Luxe Aesthetic**: Elegant design with Violet & Lavender theme.
- **Shop & Discovery**: Filter by category and price.
- **Cart Management**: Session-based cart (no login required).
- **Secure Payments**: Integrated with Paystack Inline checkout.
- **Order Notifications**: Automated order confirmation emails via Web3Forms.

## Tech Stack
- **Backend**: Django
- **Frontend**: HTML5, Vanilla CSS, JavaScript
- **Database**: SQLite
- **Integrations**: Paystack, Web3Forms

## Setup Instructions

1. **Clone the repository** (or navigate to the project folder).
2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   Create a `.env` file in the root directory (using `.env.example` as a template) and add your keys:
   ```env
   PAYSTACK_SECRET_KEY=yours
   PAYSTACK_PUBLIC_KEY=yours
   WEB3FORMS_ACCESS_KEY=yours
   ```
5. **Run Migrations**:
   ```bash
   python3 manage.py migrate
   ```
6. **Seed Products**:
   ```bash
   python3 manage.py seed_products
   ```
7. **Create Superuser** (to access `/admin/`):
   ```bash
   python3 manage.py createsuperuser
   ```
8. **Start Server**:
   ```bash
   python3 manage.py run_server
   ```

## Admin Portal
Access the admin portal at `http://127.0.0.1:8000/admin/` to manage products and view orders.
