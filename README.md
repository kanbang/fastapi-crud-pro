# FastAPI-CRUD-Pro


FastAPI-CRUD-Pro is a powerful library inspired by **[fastapi-crudrouter](https://github.com/awtkns/fastapi-crudrouter)**. It leverages FastAPI and Pydantic to automatically generate CRUD routes from simple ORM and DTO definitions. It supports advanced filtering, flexible sorting, one-to-many and many-to-many foreign key relationships, and automatic inclusion of foreign key data in queries. Currently, it supports SQLAlchemy, with Tortoise ORM support coming soon.

## Features

- **Auto-generate CRUD Routes**: Define your ORM and DTO models, and FastAPI-CRUD-Pro will handle the rest.
- **Advanced Filtering**: Supports complex query conditions to retrieve exactly the data you need.
- **Flexible Sorting**: Order your query results based on one or multiple fields.
- **Foreign Key Relationships**: Seamlessly handle one-to-many and many-to-many relationships, with automatic inclusion of related data.
- **Foreign Key Updates**: Update foreign key relationships effortlessly.
- **SQLAlchemy Support**: Fully integrated with SQLAlchemy for ORM operations.
- **Tortoise ORM Support**: Tortoise ORM support is on the way.

## Run Demo

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



## Usage

#### Example: Query Many By Filter Value And Sort

![alt query](https://raw.githubusercontent.com/kanbang/fastapi-crud-pro/master/doc/query.png)

#### Endpoint

```http
curl -X 'POST' \
  'http://localhost:8010/employee/query?sort_by=-name&relationships=false&user_data_filter=ALL_DATA&skip=0' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "department_id": 1,
  "retire": true
}'
```
#### Response 

```json
{
  "code": 0,
  "msg": "OK",
  "meta": {
    "total": 0
  },
  "data": [
    {
      "id": 3,
      "number": "003",
      "name": "name3",
      "retire": true,
      "retire_date": "2024-05-26T04:28:28.101000",
      "department": null,
      "department_id": 1,
      "teams": null,
      "teams_refids": null
    },
    {
      "id": 2,
      "number": "002",
      "name": "name2",
      "retire": true,
      "retire_date": "2024-05-26T04:29:20.640000",
      "department": null,
      "department_id": 1,
      "teams": null,
      "teams_refids": null
    },
    {
      "id": 1,
      "number": "001",
      "name": "name1",
      "retire": true,
      "retire_date": "2024-05-26T04:29:20.640000",
      "department": null,
      "department_id": 1,
      "teams": null,
      "teams_refids": null
    }
  ],
  "success": true
}
```

#### `Filtering`

#### Filtering by DTO Fields

FastAPI-CRUD-Pro allows filtering based on all fields defined in the DTO. All filter conditions are combined using logical `AND`, meaning all specified conditions must be met for a result to be included. 

#### Example: 

To filter results by strict equality on specific fields, you can pass a JSON object with the desired field values. For example:

```json
{
  "department_id": 1,
  "retire": true
}
```

In the above example, only results where `department_id` is equal to 1 and `retire` is equal to `true` will be included in the response.


#### `Sorting`

In the above example, `sort_by` is used to specify the sorting order:
- `name` sorts the results in ascending order by the `name` field.
- `-name` sorts the results in descending order by the `name` field.

#### Example: Sorting

```http
GET /employee/list?sort_by=-name
```

In the above example, `sort_by` is used to specify the sorting order:
- `name` sorts the results in ascending order by the `name` field.
- `-name` sorts the results in descending order by the `name` field.




## Quick Start
