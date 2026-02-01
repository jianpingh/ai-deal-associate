# Database Migration Guide

This guide explains how to manage database schema changes using Alembic with SQLModel.

## Prerequisites

- Alembic is already configured in `backend/alembic/`
- DATABASE_URL environment variable is set
- Virtual environment is activated

## Common Alembic Commands

| Command | Description |
|---------|-------------|
| `alembic current` | Show current database version |
| `alembic history` | View migration history |
| `alembic revision --autogenerate -m "description"` | Auto-generate migration script |
| `alembic upgrade head` | Upgrade to latest version |
| `alembic upgrade +1` | Upgrade one version |
| `alembic downgrade -1` | Rollback one version |
| `alembic downgrade <revision>` | Rollback to specific version |

## Workflow: Modifying Table Schema

### Step 1: Modify the Model File

Edit the SQLModel class in `backend/db/models/`:

```python
# Example: Add a new field to Asset model
# backend/db/models/asset.py

class Asset(SQLModel, table=True):
    __tablename__ = "assets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    name: str
    asset_type: str
    # ... existing fields ...
    
    # NEW FIELD
    new_field: Optional[str] = None
```

### Step 2: Generate Migration Script

```bash
cd backend
alembic revision --autogenerate -m "add new_field to assets"
```

This creates a new file in `alembic/versions/` like:
```
alembic/versions/xxxx_add_new_field_to_assets.py
```

### Step 3: Review the Migration Script

Always review the auto-generated migration before applying:

```python
# alembic/versions/xxxx_add_new_field_to_assets.py

def upgrade():
    op.add_column('assets', sa.Column('new_field', sa.String(), nullable=True))

def downgrade():
    op.drop_column('assets', 'new_field')
```

### Step 4: Apply the Migration

```bash
# Upgrade to latest version
alembic upgrade head

# Or upgrade just one version
alembic upgrade +1
```

### Step 5: Rollback (if needed)

```bash
# Rollback one version
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

## Common Schema Changes

### Add a New Column

```python
# In model
new_column: Optional[str] = None

# Generated migration
op.add_column('table_name', sa.Column('new_column', sa.String(), nullable=True))
```

### Add a Column with Default Value

```python
# In model
status: str = Field(default="active")

# You may need to manually edit migration for existing data
op.add_column('table_name', sa.Column('status', sa.String(), server_default='active'))
```

### Remove a Column

```python
# Delete the field from model, then:
alembic revision --autogenerate -m "remove column_name from table"
```

### Rename a Column

Auto-generate may detect this as drop + add. Manually edit:

```python
def upgrade():
    op.alter_column('table_name', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('table_name', 'new_name', new_column_name='old_name')
```

### Add an Index

```python
# In model
email: str = Field(index=True)

# Or manually
op.create_index('ix_users_email', 'users', ['email'])
```

### Add a Foreign Key

```python
# In model
deal_id: int = Field(foreign_key="deals.id", index=True)
```

## Best Practices

1. **Always review auto-generated migrations** - They may not be perfect
2. **Test migrations locally first** - Before applying to production
3. **Keep migrations small** - One logical change per migration
4. **Never edit applied migrations** - Create new ones instead
5. **Use meaningful messages** - `alembic revision -m "add user email verification"`
6. **Backup before major migrations** - Especially in production

## Troubleshooting

### Migration not detecting changes

```bash
# Make sure models are imported in alembic/env.py
from db.models import *  # Import all models
```

### Database out of sync

```bash
# Check current state
alembic current

# Stamp database to specific version (use with caution)
alembic stamp head
```

### Conflicting migrations

```bash
# Merge migration heads
alembic merge -m "merge heads" head1 head2
```

## Creating Tables from Scratch

If you need to create all tables without migrations:

```bash
cd backend
python create_tables.py
```

Or programmatically:

```python
from sqlmodel import SQLModel
from db.database import engine
from db.models import *  # Import all models

SQLModel.metadata.create_all(engine)
```

## Database Schema Overview

Current tables (24 total):

| Category | Tables |
|----------|--------|
| Core | users, deals, assets, documents |
| Property | tenants, rent_rolls, operating_statements |
| Analysis | comps, market_data, assumptions |
| Financial | financial_models, cashflow_projections, sensitivity_analyses, scenarios, loan_quotes |
| Output | deck_versions, templates |
| Chat | chat_threads, chat_messages |
| System | deal_team, audit_logs, notifications |
