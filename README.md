# FastAPI-CRUD-Pro

FastAPI-CRUD-Pro is a powerful library that leverages FastAPI and Pydantic to automatically generate CRUD routes from simple ORM and DTO definitions. It supports advanced filtering, flexible sorting, one-to-many and many-to-many foreign key relationships, and automatic inclusion of foreign key data in queries. Currently, it supports SQLAlchemy, with Tortoise ORM support coming soon.

## Features

- **Auto-generate CRUD Routes**: Define your ORM and DTO models, and FastAPI-CRUD-Pro will handle the rest.
- **Advanced Filtering**: Supports complex query conditions to retrieve exactly the data you need.
- **Flexible Sorting**: Order your query results based on one or multiple fields.
- **Foreign Key Relationships**: Seamlessly handle one-to-many and many-to-many relationships, with automatic inclusion of related data.
- **Foreign Key Updates**: Update foreign key relationships effortlessly.
- **SQLAlchemy Support**: Fully integrated with SQLAlchemy for ORM operations.
- **Tortoise ORM Support**: Tortoise ORM support is on the way.

## Test

```sh
poetry install
poetry shell
python create_sqlalchemydemo_db.py
python test_sqlalchemy_router.py

```



**Open**: <a href="http://localhost:8010/docs" target="_blank">http://localhost:8010/docs</a>

<img alt="dummy" src="https://raw.githubusercontent.com/kanbang/fastapi-crud-pro/master/doc/dummy.png">
<img alt="Employee" src="https://raw.githubusercontent.com/kanbang/fastapi-crud-pro/master/doc/Employee.png">
<img alt="Department" src="https://raw.githubusercontent.com/kanbang/fastapi-crud-pro/master/doc/department.png">
<img alt="Team" src="https://raw.githubusercontent.com/kanbang/fastapi-crud-pro/master/doc/team.png">


## Database Table Relationships

### Department

| Column | Type   | Constraints     |
|--------|--------|-----------------|
| id     | int    | PRIMARY KEY     |
| name   | string |                 |
| factor | float  |                 |

### Team

| Column | Type   | Constraints     |
|--------|--------|-----------------|
| id     | int    | PRIMARY KEY     |
| name   | string |                 |

### Employee

| Column        | Type      | Constraints                          |
|---------------|-----------|--------------------------------------|
| id            | int       | PRIMARY KEY                          |
| number        | string    | UNIQUE                               |
| name          | string    |                                      |
| retire        | boolean   | DEFAULT False                        |
| retire_date   | datetime  | DEFAULT datetime.now                 |
| department_id | int       | FOREIGN KEY (references Department)  |

### Association Table (teams_employee_table)

| Column      | Type | Constraints                          |
|-------------|------|--------------------------------------|
| team_id     | int  | PRIMARY KEY, FOREIGN KEY (references Team) |
| employee_id | int  | PRIMARY KEY, FOREIGN KEY (references Employee) |

### Relationships

- **Department** `1` : `N` **Employee**
  - One `Department` has many `Employees`.
  - One `Employee` belongs to one `Department`.

- **Team** `N` : `M` **Employee**
  - One `Team` can have many `Employees`.
  - One `Employee` can belong to many `Teams`.
  - This relationship is facilitated by the `Association Table`.

### Foreign Keys

- **Employee** table:
  - `department_id` references `Department.id`.
  - `team_id` and `employee_id` in the `Association Table` reference `Team.id` and `Employee.id` respectively.



## Quick Start
