#  E-Commerce Web Application

A simple and secure E-Commerce web application built using **Flask**, **SQLite**, HTML, and CSS.

This project demonstrates user authentication, password security, database handling, and deployment using Render.

##  Live Website

https://e-commerce-1-5z4j.onrender.com


##  Features

- ✅ User Registration
- ✅ User Login
- ✅ Secure Password Hashing
- ✅ Logout Functionality
- ✅ Forgot Password Page
- ✅ SQLite Database Integration
- ✅ Clean UI Design
- ✅ Fully Deployed on Render


##  Tech Stack

- Python 3
- Flask
- SQLite
- HTML5
- CSS3
- Gunicorn
- Render (Cloud Deployment)


##Project Structure

```
E-commerce/
│
├── app.py
├── database.db
├── requirements.txt
├── Procfile
├── README.md
│
└── templates/
    ├── login.html
    ├── register.html
    ├── forgot.html
    └── index.html
```

## ⚙️ How to Run Locally

### Clone Repository

```
git clone https://github.com/daneshreddy/E-commerce.git
```

###  Go Inside Project

```
cd E-commerce
```

### 3️⃣ Create Virtual Environment

```
python -m venv venv
```

###  Activate Virtual Environment

Windows:
```
venv\Scripts\activate
```

Mac/Linux:
```
source venv/bin/activate
```

### 5️⃣ Install Requirements

```
pip install -r requirements.txt
```

###  Run the Application

```
python app.py
```

App will run at:
```
http://127.0.0.1:5000
```

---

## Security Features

- Passwords are hashed using `werkzeug.security`
- SQL Injection prevented using parameterized queries
- Session-based login system

---

## Deployment Details

This application is deployed using:

- Render Web Service
- Gunicorn WSGI Server
- Procfile configuration

---

##  Author

**Danesh Reddy**

##  Support

If you like this project, give it a ⭐ on GitHub!
