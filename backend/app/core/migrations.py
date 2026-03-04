"""
Database migration utilities and documentation.

MIGRATION STRATEGY:
==================

1. INITIAL SETUP
   - Database schema is managed by Alembic migrations (not SQLModel.metadata.create_all())
   - All schema changes must be made via migrations
   - Migrations are in alembic/versions/ directory

2. CREATING MIGRATIONS
   - Make model changes in app/models/
   - Run: alembic revision --autogenerate -m "Description of change"
   - This creates a new migration file in alembic/versions/
   - ALWAYS review the generated migration for correctness
   - Edit the migration file if needed

3. MIGRATION CONSTRAINTS
   - Forward migrations can only add:
     * Nullable columns (no default required)
     * Columns with defaults
     * New tables
     * Indexes, constraints on existing columns
   - Forward migrations CANNOT:
     * Drop columns (use backward compatibility with deprecated_at field)
     * Drop tables
     * Add NOT NULL columns without defaults
     * Rename columns (create new, migrate data, drop old)
   - All backward migrations must be reversible (don't drop important data)

4. RUNNING MIGRATIONS
   - Remote Dev: Docker containers handle migrations automatically
   - Local Dev: Run before starting server:
     * cd backend
     * alembic upgrade head
   - Testing: Each migration must be reversible:
     * alembic upgrade head
     * alembic downgrade -1
     * alembic upgrade head (verify no errors)

5. SCHEMA CHANGES (STEP-BY-STEP EXAMPLE)
   - Adding a new required field:
     1. Add field as nullable + default in model
     2. Run migration
     3. Deploy migration
     4. Populate existing records with values
     5. Run second migration to add NOT NULL constraint
   - Renaming a column:
     1. Add new column with same type
     2. Copy data
     3. Update code to use new column
     4. Drop old column (backward compat step)
   - Removing a column:
     1. Deprecate in code (don't use)
     2. Keep column in DB (backward compat)
     3. Remove in future major version

6. DEPLOYMENT PROCESS
   - Pre-deployment:
     * Run alembic upgrade head locally to test
     * Review migrations for data loss
   - During deployment:
     * Run alembic upgrade head on production DB
     * Deploy new code
   - Post-deployment:
     * Monitor logs for database errors
     * Check migration status

7. TROUBLESHOOTING
   - To see current migration state: alembic current
   - To see history: alembic history
   - To check for pending migrations: alembic current vs alembic heads
   - To repair a merge conflict: alembic merge --auto
   - To manually mark migration as applied: alembic stamp <revision>
"""

from typing import List, Tuple
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine
from app.config import settings


def get_migration_script_directory() -> ScriptDirectory:
    """Get the Alembic script directory."""
    config = Config("alembic.ini")
    return ScriptDirectory.from_config(config)


def get_current_revision() -> str:
    """Get the current database revision."""
    engine = create_engine(settings.sync_database_url)
    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        return context.get_current_revision()


def get_head_revisions() -> List[str]:
    """Get the head revisions."""
    script = get_migration_script_directory()
    return [revision for revision in script.get_heads()]


def get_migration_history() -> List[Tuple[str, str]]:
    """Get migration history as list of (revision, message) tuples."""
    script = get_migration_script_directory()
    history = []
    for revision in script.walk_revisions():
        history.append((revision.revision, revision.doc))
    return history


def validate_migration_constraints(migration_content: str) -> List[str]:
    """
    Validate that a migration follows best practices.
    
    Args:
        migration_content: The content of the migration file
        
    Returns:
        List of violations found (empty if valid)
    """
    violations = []
    
    # Check for direct column drops
    if "DROP COLUMN" in migration_content and "deprecated" not in migration_content.lower():
        violations.append("Dropping columns violates backward compatibility. Use deprecated_at pattern instead.")
    
    # Check for table drops
    if "DROP TABLE" in migration_content:
        violations.append("Dropping tables violates backward compatibility. Use soft deletes instead.")
    
    # Check for NOT NULL without default on new columns
    if "nullable=False" in migration_content and "server_default" not in migration_content:
        # This is a heuristic - may have false positives
        violations.append("Adding NOT NULL column without default may fail on existing data. Consider using server_default or making it nullable first.")
    
    return violations


def print_migration_info() -> None:
    """Print current migration status to console."""
    current = get_current_revision()
    heads = get_head_revisions()
    history = get_migration_history()
    
    print("\n" + "="*60)
    print("DATABASE MIGRATION STATUS")
    print("="*60)
    print(f"Current Revision: {current or 'None (database is at initial state)'}")
    print(f"Head Revisions: {', '.join(heads)}")
    print(f"\nMigration History ({len(history)} migrations):")
    for i, (revision, message) in enumerate(reversed(history), 1):
        marker = " <- CURRENT" if revision == current else ""
        print(f"  {i}. {revision}: {message}{marker}")
    print("="*60 + "\n")
