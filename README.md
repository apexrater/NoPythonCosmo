# Library Management System

## Overview

This project is a Library Management System built with FastAPI and MongoDB. It provides a set of APIs to manage library operations such as adding, updating, and deleting books, managing users, and handling borrowing and returning of books.

## Tech Stack

- Language: Python
- Framework: FastAPI
- Database: MongoDB (MongoDB Atlas M0 Free Cluster)

## Setup

1. **Clone the repository:**

   ```
   git clone <repository_url>
   cd library_management_system
   ```

2. **Configure MongoDB**

- Sign up for MongoDB Atlas and create an M0 Free Tier cluster.
- Obtain the connection string.
- Replace the connection string in the code where AsyncIOMotorClient is used to connect to the database.

## Run the Application

```
uvicorn main:app --reload
```
