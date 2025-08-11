# Quickstart Guide: Incorporating this DB Migration System into your UBC CIC Project

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
    code: lambda.Code.fromAsset("lambda/db_setup"), // MAKE SURE IT USES THIS SPECIFIC FOLDER!
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
            "user_id" uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
            "user_email" varchar UNIQUE,
            "username" varchar,
            "first_name" varchar,
            "last_name" varchar,
            "time_account_created" timestamp,
            "roles" varchar[],
            "last_sign_in" timestamp
        );



        -- Add other initial schema tables and foreign key constraints as needed

    """
```

and alter the SQL return string to suit your database schema as desired.

### Now, you can either redeploy your project or create a new deployment, and this database migrations system will be successfully incorporated!

## Step 4 - Altering your schema

To take full advantage of database migrations, we should be able to alter our database schema without having to create a full, new deployment; we should only need to redeploy to an existing deployment.

You can now do this with ease, using your newly-added database migration system!

For a detailed guide on this, refer to the [Database Modification Guide](./databaseModificationGuide.md) (which you should now include in the documentation of your current project)
