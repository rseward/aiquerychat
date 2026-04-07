# 1) Add Schema Generation Support

## Structure into adapters

As needed create a adapter per database to handle db specific nuances

- schema/postgres.py
- schema/mssql.py
- schema/mysql.py

Plug in support for third party database not covered by built adapter modules



