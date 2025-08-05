📁 e-commerce/README.md
# 🛒 E-Commerce Backend (Django)

This project is part of **Project Nexus**, the capstone for the ProDev Backend Engineering program. It is a fully functional backend system for an e-commerce platform, focused on scalability, performance, and usability.

## 🚀 Project Goals

- Build a robust backend for managing product catalogs, user accounts, and orders.
- Implement authentication using JWT.
- Provide filtering, sorting, and pagination for efficient product browsing.
- Expose APIs for frontend integration with clear documentation.

## 🛠️ Tech Stack

- **Django**
- **Django REST Framework**
- **PostgreSQL**
- **JWT Authentication**
- **Swagger/OpenAPI**

## 🔑 Key Features

- **User Management**: Register, login, and JWT-based authentication.
- **Product Management**: CRUD operations for product catalog.
- **Pagination, Filtering & Sorting**: Query products efficiently via API.
- **Order Management**: Add to cart, checkout flow (optional/extendable).
- **Swagger Docs**: Auto-generated API documentation.

## 🔧 Setup Instructions

1. **Clone the repository**

```bash
   git clone https://github.com/yourusername/project-nexus.git
   cd project-nexus/e-commerce/django
Create virtual environment & install dependencies

bash
Copy
Edit
python -m venv env
source env/bin/activate
pip install -r requirements.txt
Apply migrations

bash
Copy
Edit
python manage.py migrate
Run development server

bash
Copy
Edit
python manage.py runserver
Access API Docs

Swagger UI: http://localhost:8000/api/docs/

📂 Project Structure
bash
Copy
Edit
e-commerce/
├── django/
│   ├── ecommerce_project/
│   ├── products/
│   ├── users/
│   ├── orders/
│   └── ...