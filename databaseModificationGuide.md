# Database Migration Guide

This guide explains how to modify your database schema using the migration system.

## Adding New Tables or Schema Changes

To add new tables, columns, or modify existing schema:

1. Create a new `.sql` file in the `migrations/` directory
2. Use sequential numbering: `002_add_products_table.sql`, `003_add_user_preferences.sql`, etc.
3. Write your SQL migration code
4. Deploy your application

### Example Migration File

Create `migrations/002_add_products_table.sql`:

```sql
-- Add products table
CREATE TABLE IF NOT EXISTS "products" (
    "id" uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    "name" varchar NOT NULL,
    "price" decimal(10,2),
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_products_name ON "products" ("name");
```

### Adding Columns to Existing Tables

Create `migrations/003_add_user_phone.sql`:

```sql
-- Add phone column to users table
ALTER TABLE "users" 
ADD COLUMN IF NOT EXISTS "phone" varchar;
```

## How It Works

- Migration files are executed in numerical order
- Each migration is tracked in the `schema_migrations` table
- Migrations are only applied once (idempotent)
- Works with both new and existing deployments
- Auto-numbering for unnumbered files

## Best Practices

- Use sequential numbering for migration files
- Include `IF NOT EXISTS` for CREATE statements
- Use `ADD COLUMN IF NOT EXISTS` for column additions
- Write descriptive migration names
- Test migrations on development environment first
- Keep migrations small and focused