# Database Migration System

A simple, drag-and-drop database migration system for AWS Lambda projects using PostgreSQL.

## Quick Setup

1. Copy the `db_setup` folder to your project's `lambda/` directory
2. Configure your CDK stack (see Integration section)
3. Add your initial schema to `migrations/001_initial_schema.sql`
4. Deploy your application

## Integration with CDK

Add this configuration to your database stack file:

```typescript
const initializerLambda = new triggers.TriggerFunction(
  this,
  `${id}-triggerLambda`,
  {
    description: `Database initializer and migration runner - ${new Date().toISOString()}`,
    functionName: `${id}-initializerFunction`,
    runtime: lambda.Runtime.PYTHON_3_9,
    handler: "initializer.handler",
    timeout: Duration.seconds(300),
    memorySize: 512,
    environment: {
      DB_SECRET_NAME: db.secretPathAdminName,
      DB_USER_SECRET_NAME: db.secretPathUser.secretName, // Optional
      DB_PROXY: db.secretPathTableCreator.secretName, // Optional
    },
    vpc: db.dbInstance.vpc,
    code: lambda.Code.fromAsset("lambda/db_setup"),
    layers: [psycopgLambdaLayer],
    role: lambdaRole,
  }
);
```

## Environment Variables

- `DB_SECRET_NAME` (required): AWS Secrets Manager secret containing database credentials
- `DB_USER_SECRET_NAME` (optional): Secret name for storing limited user credentials
- `DB_PROXY` (optional): Secret name for storing table creator credentials
- `CREATE_USERS` (optional): Set to "false" to skip user creation (default: "true")

## Initial Schema Setup

Edit `migrations/001_initial_schema.sql` with your database schema:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS "users" (
    "id" uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    "email" varchar UNIQUE,
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "products" (
    "id" uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    "name" varchar NOT NULL,
    "price" decimal(10,2),
    "user_id" uuid REFERENCES "users"("id")
);
```

## Adding New Migrations

Create numbered SQL files in the `migrations/` directory:

- `002_add_orders_table.sql`
- `003_add_user_preferences.sql`
- `004_add_indexes.sql`

Each file runs once and is tracked automatically. Numbers are technically not needed and will work without them, but it is best practice to include numberings for migration tracking.

## Features

- **Idempotent**: Migrations run only once
- **Auto-numbering**: Unnumbered files get sequential numbers
- **Existing deployments**: Automatically handles databases without migration tracking
- **User management**: Optional creation of limited-privilege database users
- **Lambda-optimized**: Works in serverless environments

For detailed migration examples, see [Database Modification Guide](./databaseModificationGuide.md).
