"""Add order lifecycle timestamps and inventory transactions

Revision ID: 3c4d5e6f7890
Revises: 2b3c4d5e6f78
Create Date: 2026-03-04 11:00:00.000000

This migration adds:
- Order lifecycle timestamp columns (paid_at, processing_at, shipped_at, delivered_at, cancelled_at)
- InventoryTransaction table for stock audit trail
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '3c4d5e6f7890'
down_revision: Union[str, None] = '2b3c4d5e6f78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add order lifecycle fields and inventory transaction table."""
    
    # ========== ADD ORDER LIFECYCLE TIMESTAMPS ==========
    
    # Add lifecycle timestamp columns to Order table
    op.add_column('order', sa.Column('paid_at', sa.DateTime(), nullable=True))
    op.add_column('order', sa.Column('processing_at', sa.DateTime(), nullable=True))
    op.add_column('order', sa.Column('shipped_at', sa.DateTime(), nullable=True))
    op.add_column('order', sa.Column('delivered_at', sa.DateTime(), nullable=True))
    op.add_column('order', sa.Column('cancelled_at', sa.DateTime(), nullable=True))
    
    # ========== CREATE INVENTORY TRANSACTION TABLE ==========
    
    op.create_table(
        'inventorytransaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('variant_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(), nullable=False),
        sa.Column('quantity_change', sa.Integer(), nullable=False),
        sa.Column('quantity_after', sa.Integer(), nullable=False),
        sa.Column('reference_type', sa.String(), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('admin_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['product.id']),
        sa.ForeignKeyConstraint(['variant_id'], ['productvariant.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.CheckConstraint('quantity_after >= 0', name='ck_inventorytransaction_quantity_nonnegative')
    )
    
    # ========== CREATE INDEXES FOR PERFORMANCE ==========
    
    # Index on product_id for querying transaction history
    op.create_index(
        'ix_inventorytransaction_product',
        'inventorytransaction',
        ['product_id']
    )
    
    # Index on variant_id for querying transaction history
    op.create_index(
        'ix_inventorytransaction_variant',
        'inventorytransaction',
        ['variant_id']
    )
    
    # Index on created_at for time-based queries
    op.create_index(
        'ix_inventorytransaction_created',
        'inventorytransaction',
        ['created_at']
    )
    
    # Index on (variant_id, created_at) for variant history queries
    op.create_index(
        'ix_inventorytransaction_variant_created',
        'inventorytransaction',
        ['variant_id', sa.text('created_at DESC')]
    )


def downgrade() -> None:
    """Remove order lifecycle fields and inventory transaction table."""
    
    # Drop indexes
    op.drop_index('ix_inventorytransaction_variant_created', table_name='inventorytransaction')
    op.drop_index('ix_inventorytransaction_created', table_name='inventorytransaction')
    op.drop_index('ix_inventorytransaction_variant', table_name='inventorytransaction')
    op.drop_index('ix_inventorytransaction_product', table_name='inventorytransaction')
    
    # Drop inventory transaction table
    op.drop_table('inventorytransaction')
    
    # Remove order lifecycle columns
    op.drop_column('order', 'cancelled_at')
    op.drop_column('order', 'delivered_at')
    op.drop_column('order', 'shipped_at')
    op.drop_column('order', 'processing_at')
    op.drop_column('order', 'paid_at')
