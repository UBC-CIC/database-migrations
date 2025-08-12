# Database Migration Guide

This guide explains how to modify your database schema using the Node.js migration system.

## Adding New Tables or Schema Changes

To add new tables, columns, or modify existing schema:

1. Create a new `.js` file in the `lambda/db_setup/migrations/` directory
2. Use sequential numbering: `002_add_products_table.js`, `003_add_user_preferences.js`, etc.
3. Write your migration using node-pg-migrate format
4. Deploy your application

### Example Migration File

Create `migrations/002_add_products_table.js`:

```javascript
exports.up = (pgm) => {
  // Add products table
  pgm.createTable(
    "products",
    {
      id: {
        type: "uuid",
        primaryKey: true,
        default: pgm.func("uuid_generate_v4()"),
      },
      name: { type: "varchar", notNull: true },
      price: { type: "decimal(10,2)" },
      created_at: { type: "timestamp", default: pgm.func("CURRENT_TIMESTAMP") },
    },
    { ifNotExists: true }
  );

  // Add index for better performance
  pgm.createIndex("products", "name", { name: "idx_products_name" });
};

exports.down = (pgm) => {
  pgm.dropTable("products", { ifExists: true, cascade: true });
};
```

### Adding Columns to Existing Tables

Create `migrations/003_add_user_phone.js`:

```javascript
exports.up = (pgm) => {
  // Add phone column to users table
  pgm.addColumn("users", {
    phone: { type: "varchar" },
  });
};

exports.down = (pgm) => {
  pgm.dropColumn("users", "phone");
};
```

## How It Works

- Migration files are executed in alphabetical order
- Each migration is tracked in the `pgmigrations` table
- Migrations are only applied once (idempotent)
- Works with both new and existing deployments
- Uses node-pg-migrate for safe schema changes

## Common Migration Operations

### Creating Tables

```javascript
exports.up = (pgm) => {
  pgm.createTable(
    "table_name",
    {
      id: { type: "uuid", primaryKey: true },
      name: { type: "varchar", notNull: true },
    },
    { ifNotExists: true }
  );
};
```

### Adding Columns

```javascript
exports.up = (pgm) => {
  pgm.addColumn("table_name", {
    new_column: { type: "varchar" },
  });
};
```

### Creating Indexes

```javascript
exports.up = (pgm) => {
  pgm.createIndex("table_name", "column_name");
};
```

### Adding Foreign Keys

```javascript
exports.up = (pgm) => {
  pgm.addConstraint("child_table", "fk_parent", {
    foreignKeys: {
      columns: "parent_id",
      references: "parent_table(id)",
    },
  });
};
```

## Best Practices

- Use sequential numbering for migration files (001*, 002*, etc.)
- Include `{ ifNotExists: true }` for CREATE operations
- Always write both `up` and `down` functions
- Write descriptive migration names
- Test migrations on development environment first
- Keep migrations small and focused
- Use node-pg-migrate helpers instead of raw SQL when possible
  -Follow the node-pg-migrate documentation found here: https://salsita.github.io/node-pg-migrate/migrations/tables
