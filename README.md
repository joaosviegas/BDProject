<h1 align="center"> Database Project </h1>

This project was developed for the "Bases de Dados" course @IST - Instituto Superior Técnico (2024/2025) and is organized in two main parts: database modeling and development of a RESTful API.

## Project Structure

### 📁 entrega-01-76
The first delivery focused on the **design and analysis** of the database:
- Includes an **E-A (Entity-Association) model** of the aviation domain.
- Conversion of the **E-A model** to it's respective **Relational Model**.
- Contains **Relational Algebra exercises** analyzing operations over the schema.
- No implementation or code was required at this stage.

### 📁 entrega-02-76
The second delivery contains the **implemented solution**:
- `/data`: Folder with the `populate.sql` file to populate the PostgreSQL database according to the project's constraints and coverage criteria.
- `/app`: A Python Flask RESTful API to interact with the database.
- `E2-report-76.ipynb`: Jupyter Notebook with answers and analysis related to integrity constraints, materialized views, OLAP queries, and indexing.

## Technologies Used

- **PostgreSQL**: Main relational database system used to implement the schema, enforce integrity, and perform analytical queries.
- **Python**: Scripting language used for the API and data handling.
- **Flask**: Framework used to build the RESTful web service.
- **psycopg2**: PostgreSQL adapter for Python, used for database interactions.
- **Jupyter Notebook**: Used to document and run analytical SQL queries with explanations.

## API Overview

The RESTful API includes endpoints such as:
- `/` – List all airports
- `/voos/<partida>/` – Show flights departing from an airport
- `/voos/<partida>/<chegada>/` – Show next available flights between two airports
- `/compra/<voo>/` – Handle ticket purchases
- `/checkin/<bilhete>/` – Automatically assign a seat during check-in

All operations are **transactional**, protected against **SQL injection**, and return **JSON**-formatted responses.

## Notes

- The API was tested and deployed in the course-provided Docker environment.
- All SQL code has been validated for execution in the lab workspace.
