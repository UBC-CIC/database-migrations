# Quickstart Guide: Incorporating this DB Migration System into your UBC CIC Project

\*NOTE: This guide assumes you're using the current CDK architecture used at the CIC as of July 29th, 2025. If not, adjust steps accordingly.

## Step 1 - Adding the necessary files

Download the `db_setup` folder provided in this repository, and add it to the `./cdk/lambda/` directory of your current project.

## Step 2 - Integrating the new files with your database stack

Navigate to the file in which you configure your database stack and invoke its initializer function to populate and create tables. Alter the code to point towards the `lambda/db_setup` directory for your intializer function.

For the current project architecture at the CIC (at the time of writing this), this can be found at `./cdk/lib/dbFlow-stack.ts`, in the following code snippet:

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
      DB_USER_SECRET_NAME: db.secretPathUser.secretName,
      DB_PROXY: db.secretPathTableCreator.secretName,
    },
    vpc: db.dbInstance.vpc,
    code: lambda.Code.fromAsset("lambda/db_setup"), // MAKE SURE THIS LINE IS CONFIGURED AS SHOWN
    layers: [psycopgLambdaLayer],
    role: lambdaRole,
  }
);
```

## Step 3 - Setting up your initial schema

Navigate back to the `./cdk/lambda/db_setup` directory, and open the `migrations.py` file. Scroll down to the following function:

```python
def get_initial_schema():
    """Return the initial schema SQL"""
    return """
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

*Note: This function will only run once per deployment. Once initialized, your schema cannot be altered by the same get_initial_schema() function, but should instead be altered another way. See the next step for instructions on how to alter your schema.

## Step 4 - Altering your schema

To take full advantage of database migrations, we should be able to alter our database schema without having to create a full, new deployment; we should only need to redeploy to an existing deployment.

You can now do this with ease, using your newly-added database migration system!

For a detailed guide on this, refer to the [Database Modification Guide](./databaseModificationGuide.md) (which you should now include in the documentation of your current project)
