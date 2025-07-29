# How to Add a New Table to the Database

This guide explains how to add a new table to the database in the Virtual Care Interaction project.

## Adding a New Table

To add a new tables/columns or alter/remove existing ones, you only need to modify the `migrations.py` file:

1. Define a function that returns the SQL for your new table
2. Register the migration in the `get_all_migrations()` function

A (commented-out) example exists in the provided `migrations.py` file, as shown below:

### Example

```python
# 1. Define a function that returns the SQL for your new table. Make a new function for every change!
def get_example_table_sql():
    """SQL for creating an example table and inserting dummy rows"""
    return """
    -- Create a generic example table if it doesn't already exist
    CREATE TABLE IF NOT EXISTS example_table (
        id    SERIAL PRIMARY KEY,
        name  TEXT   NOT NULL,
        flag  BOOLEAN DEFAULT FALSE
    );
    """

# 2. In the get_all_migrations function, add this line that invokes the newly defined function above:
register_migration("add_example_table", get_example_table_sql())

# Add more calls to register_migration() if you have more SQL functions.
```

That's it! The migration will be applied automatically during your next (re)deployment.

<!-- \*Note: `register_migration()` is an idempotent function, which, in this context, means that it will only apply your defined SQL function once. This is a good thing, as it means you can leave and commit your code as-is, no changes are required after this point, as there is no risk of duplicate tables if you redeploy! -->

## How It Works

- The system automatically assigns version numbers based on registration order
- Migrations are tracked in the database, so they're only applied once (idempotency)
- The system works in both new deployments and existing deployments
- No need to worry about file system access in Lambda environments

## Best Practices

- Use descriptive names for your migration functions and registrations
- Include `IF NOT EXISTS` in your CREATE TABLE statements
- For column additions, check if the column exists before adding it
- Always include appropriate foreign key constraints
