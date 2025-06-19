# 🛡️ TA Duty Maintenance System

> A full-stack Django web application designed to streamline the allocation and management of Teaching Assistant (TA) duties in academic institutions.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [System Roles & Permissions](#system-roles--permissions)
- [System Architecture](#system-architecture)
- [Screenshots](#screenshots)
- [Setup Instructions](#setup-instructions)
- [Future Enhancements](#future-enhancements)
- [Contributors](#contributors)
- [License](#license)

---

## 🧠 Overview

Managing TA duties manually? Say goodbye to Excel chaos and hello to centralized control.

The **TA Duty Maintenance System** is a role-based academic workflow management platform that brings together Admins, Professors, Teaching Assistants, and Students under one roof. Whether it’s scheduling TA duties, enrolling in courses, or submitting assignments — this system does it all.

---

## ✨ Key Features

| Category                 | Features                                                                 |
|--------------------------|--------------------------------------------------------------------------|
| 👥 User Management        | Self-registration (with ID verification), Role-based Access             |
| 🗂️ TA Assignment          | Admin assigns TAs to Professors                                          |
| 📅 Schedule Management   | Professors schedule/edit/cancel TA duties                               |
| 📣 Notifications          | In-app + email alerts for upcoming duties/assignments                   |
| ✅ Duty Logging           | TAs mark completed duties                                                |
| 📚 Course Enrollment      | Students enroll in courses                                               |
| 📝 Assignment Submissions| Students submit assignments, TAs/Professors can grade                   |
| 🛡️ Role Dashboards       | Unique dashboards for Admin, Prof, TA & Student                          |
| 🔐 Secure Auth            | Login, logout, password reset, bcrypt hashed passwords                  |

---

## 🧰 Tech Stack

| Layer        | Technology           |
|--------------|----------------------|
| Backend      | Django (Python)      |
| Frontend     | HTML, CSS, JavaScript |
| Database     | SQLite               |
| Auth System  | Django Auth + bcrypt |
| Hosting      | (Optional) PythonAnywhere/Heroku/Railway |

---

## 🔐 System Roles & Permissions

| Feature                      | Admin | Professor | TA | Student |
|------------------------------|:-----:|:---------:|:--:|:-------:|
| Assign TAs                   | ✅    | ❌        | ❌ | ❌      |
| Create/Edit Schedules        | ❌    | ✅        | ❌ | ❌      |
| Submit Assignments           | ❌    | ❌        | ❌ | ✅      |
| Enroll in Courses            | ❌    | ❌        | ❌ | ✅      |
| View Assigned Duties         | ✅    | ✅        | ✅ | ❌      |
| Notifications (in-app/email) | ❌    | ❌        | ✅ | ✅      |
| Role Permissions Mgmt        | ✅    | ❌        | ❌ | ❌      |

---

## 🧩 System Architecture

- **Architecture Pattern**: Django MVT (Model-View-Template)
- **Database Design**: Normalized using ERD with entities like Users, Roles, TA Assignments, Courses, Submissions, etc.
- **DFD Levels**:
  - Level 0: System Context Overview
  - Level 1: Breakdown of role-wise modules
  - Level 2: Deep dive into core processes like TA scheduling and grading

---

## 📸 Screenshots (from Appendix A of the Report)

> *(You can embed actual screenshots here in Markdown if uploading to GitHub Pages or similar)*

- Login Page
- Admin Dashboard
- Professor's TA Schedule Panel
- TA’s Duty Log
- Student Course Enrollment & Assignment Page

---

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.8+
- Git
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/<your-username>/ta-duty-manager.git
cd ta-duty-manager

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Migrate DB
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver
```
### here are the links to:
- #### *Problem Statement:* [Mini_Project_PS.pdf](https://github.com/user-attachments/files/20813973/Mini_Project_PS.pdf)
- #### *SRS:* [Mini_Project_SRS.pdf](https://github.com/user-attachments/files/20813972/Mini_Project_SRS.pdf)
- #### *Project Report:* [Mini_Project_Report.pdf](https://github.com/user-attachments/files/20813971/Mini_Project_Report.pdf)
