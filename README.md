# Quickstart Guide: Incorporating this DB Migration System into your AWS CDK Project

A simple, drag-and-drop database migration system for AWS Lambda projects using node-pg-migrate.

## Quick Setup

1. Copy the `cdk/lambda/db_setup` folder to your project's `lambda/` directory
2. Copy the `cdk/layers/node-pg-migrate.zip` layer to your project's `layers/` directory
3. Copy the `cdk/lib/dbFlow-stack.ts` to your project's CDK lib directory
4. Configure your CDK stack (see Integration section)
5. Add your initial schema to `migrations/001_initial_schema.js`
6. Deploy your application

## Integration with CDK

Add this configuration to your main CDK app or stack file:

```typescript
import { DatabaseMigrationStack } from "./lib/dbFlow-stack";

// In your main stack or app
const migrationStack = new DatabaseMigrationStack(this, "DatabaseMigrations", {
  vpc: yourVpc, // Your existing VPC
  dbSecretName: "your-db-admin-secret-name", // Your RDS admin secret
  userSecretName: "your-db-user-secret-name", // Optional: for app user
  tableCreatorSecretName: "your-db-creator-secret-name", // Optional: for table creator
});
```

### Minimal Setup (Migrations Only)

If you only want migrations without user creation:

```typescript
const migrationStack = new DatabaseMigrationStack(this, "DatabaseMigrations", {
  vpc: yourVpc,
  dbSecretName: "your-db-admin-secret-name",
  skipUserCreation: true, // Skip automatic user creation
});
```

## Environment Variables

The system automatically configures these environment variables:

- `DB_SECRET_NAME` (required): AWS Secrets Manager secret containing database credentials
- `DB_USER_SECRET_NAME` (optional): Secret name for storing limited user credentials
- `DB_PROXY` (optional): Secret name for storing table creator credentials
- `CREATE_USERS` (optional): Set to "false" to skip user creation (default: "true")

## Initial Schema Setup

Edit `migrations/001_initial_schema.js` with your database schema:

```javascript
exports.up = (pgm) => {
  // Create UUID extension
  pgm.createExtension("uuid-ossp", { ifNotExists: true });

  // Create your tables
  pgm.createTable(
    "users",
    {
      user_id: {
        type: "uuid",
        primaryKey: true,
        default: pgm.func("uuid_generate_v4()"),
      },
      user_email: { type: "varchar", unique: true },
      username: { type: "varchar" },
      first_name: { type: "varchar" },
      last_name: { type: "varchar" },
      time_account_created: { type: "timestamp" },
      roles: { type: "varchar[]" },
      last_sign_in: { type: "timestamp" },
    },
    { ifNotExists: true }
  );

  // Add other initial schema tables and foreign key constraints as needed
};

exports.down = (pgm) => {
  pgm.dropTable("users", { ifExists: true, cascade: true });
  pgm.dropExtension("uuid-ossp", { ifExists: true });
};
```

### Now, you can either redeploy your project or create a new deployment, and this database migrations system will be successfully incorporated!

## Altering your schema

To take full advantage of database migrations, you should be able to alter your database schema without having to create a full, new deployment; you should only need to redeploy to an existing deployment.

You can now do this with ease, using your newly-added database migration system!

For a detailed guide on this, refer to the [Database Modification Guide](./databaseModificationGuide.md) (which you should now include in the documentation of your current project)

## Features

- ✅ Automatic migration tracking using `pgmigrations` table
- ✅ Idempotent deployments - safe to run multiple times
- ✅ Automatic user role creation (optional)
- ✅ VPC support for secure database connections
- ✅ Production-ready error handling and rollback
- ✅ CloudWatch logging for debugging

## User Roles Created (if enabled)

- `app_rw`: Read/write access to all tables
- `app_tc`: Table creator with full schema modification rights

Credentials are automatically rotated and stored in Secrets Manager on each deployment.

## Configuration Options

### Required Parameters

- `vpc`: The VPC where your database resides
- `dbSecretName`: AWS Secrets Manager secret containing admin database credentials

### Optional Parameters

- `userSecretName`: Secret name for storing read/write user credentials
- `tableCreatorSecretName`: Secret name for storing table creator credentials
- `skipUserCreation`: Skip automatic user creation (default: false)
- `lambdaRole`: Custom IAM role for the Lambda function
- `timeoutSeconds`: Lambda timeout in seconds (default: 300)
- `memorySize`: Lambda memory in MB (default: 512)

## Troubleshooting

- **Migration fails**: Check CloudWatch logs for the Lambda function
- **Permission errors**: Ensure the Lambda role has access to Secrets Manager and VPC
- **Connection timeouts**: Increase the Lambda timeout or check VPC/security group configuration
- **Migration files not found**: Ensure the `lambda/db_setup` folder structure is correct