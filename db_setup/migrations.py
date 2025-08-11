import os
import subprocess
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def initialize_existing_deployment(db_secret):
    """Mark existing migrations as applied for deployments without migration tracking"""
    import psycopg2
    import glob
    
    try:
        connection = psycopg2.connect(
            user=db_secret["username"],
            password=db_secret["password"],
            host=db_secret["host"],
            dbname=db_secret["dbname"]
        )
        cursor = connection.cursor()
        
        # Check if migration table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'schema_migrations'
            );
        """)
        migration_table_exists = cursor.fetchone()[0]
        
        # Check if any tables exist in the database
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE';
        """)
        table_count = cursor.fetchone()[0]
        
        # If tables exist but no migration tracking, initialize it
        if table_count > 0 and not migration_table_exists:
            logger.info("Existing deployment detected without migration tracking. Initializing...")
            
            # Create migrations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS "schema_migrations" (
                    "id" SERIAL PRIMARY KEY,
                    "migration_name" VARCHAR(255) UNIQUE NOT NULL,
                    "applied_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Get all migration files
            current_dir = os.path.dirname(__file__)
            migrations_dir = os.path.join(current_dir, 'migrations')
            sql_files = glob.glob(os.path.join(migrations_dir, '*.sql'))
            
            # Mark all existing migration files as applied
            for file_path in sorted(sql_files):
                filename = os.path.basename(file_path)
                migration_name = filename.replace('.sql', '')
                
                cursor.execute(
                    "INSERT INTO schema_migrations (migration_name) VALUES (%s) ON CONFLICT (migration_name) DO NOTHING",
                    (migration_name,)
                )
            
            connection.commit()
            logger.info(f"Marked {len(sql_files)} existing migrations as applied")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        logger.error(f"Error initializing existing deployment: {str(e)}")
        raise e

def prepare_migrations_directory():
    """Prepare migrations in /tmp with auto-numbering"""
    import glob
    import shutil
    
    current_dir = os.path.dirname(__file__)
    source_migrations_dir = os.path.join(current_dir, 'migrations')
    temp_migrations_dir = '/tmp/migrations'
    
    # Create temp directory
    os.makedirs(temp_migrations_dir, exist_ok=True)
    
    # Get all SQL files
    sql_files = glob.glob(os.path.join(source_migrations_dir, '*.sql'))
    
    numbered_files = []
    unnumbered_files = []
    
    # Separate numbered and unnumbered files
    for file_path in sql_files:
        filename = os.path.basename(file_path)
        if filename[:3].isdigit() and filename[3] == '_':
            numbered_files.append((file_path, int(filename[:3])))
        else:
            unnumbered_files.append(file_path)
    
    # Find the next available number
    if numbered_files:
        next_number = max(num for _, num in numbered_files) + 1
    else:
        next_number = 1
    
    # Copy all files to temp directory with proper numbering
    for file_path, _ in numbered_files:
        filename = os.path.basename(file_path)
        shutil.copy2(file_path, os.path.join(temp_migrations_dir, filename))
    
    for file_path in sorted(unnumbered_files):
        filename = os.path.basename(file_path)
        new_filename = f"{next_number:03d}_{filename}"
        
        logger.info(f"Auto-numbering: {filename} -> {new_filename}")
        shutil.copy2(file_path, os.path.join(temp_migrations_dir, new_filename))
        next_number += 1
    
    return temp_migrations_dir

def run_migrations(db_secret):
    """Run migrations using Python (node-pg-migrate style)"""
    import psycopg2
    import glob
    
    try:
        # Prepare migrations with auto-numbering in /tmp
        migrations_dir = prepare_migrations_directory()
        
        # Initialize existing deployments first
        initialize_existing_deployment(db_secret)
        
        # Connect to database
        connection = psycopg2.connect(
            user=db_secret["username"],
            password=db_secret["password"],
            host=db_secret["host"],
            dbname=db_secret["dbname"]
        )
        cursor = connection.cursor()
        
        # Create migrations table (matching existing schema)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "schema_migrations" (
                "id" SERIAL PRIMARY KEY,
                "migration_name" VARCHAR(255) UNIQUE NOT NULL,
                "applied_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        connection.commit()
        
        # Get all migration files
        sql_files = glob.glob(os.path.join(migrations_dir, '*.sql'))
        
        # Run migrations in order
        for file_path in sorted(sql_files):
            filename = os.path.basename(file_path)
            migration_name = filename.replace('.sql', '')
            
            # Check if migration already applied
            cursor.execute("SELECT COUNT(*) FROM schema_migrations WHERE migration_name = %s", (migration_name,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                logger.info(f"Applying migration: {migration_name}")
                
                # Read and execute migration
                with open(file_path, 'r') as f:
                    migration_sql = f.read()
                
                cursor.execute(migration_sql)
                
                # Record migration as applied
                cursor.execute(
                    "INSERT INTO schema_migrations (migration_name) VALUES (%s)",
                    (migration_name,)
                )
                connection.commit()
                logger.info(f"Migration {migration_name} applied successfully")
            else:
                logger.info(f"Migration {migration_name} already applied, skipping")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        raise e