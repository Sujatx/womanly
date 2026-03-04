"""Add database constraints and indexes

Revision ID: 2b3c4d5e6f78
Revises: 18b397119ce8
Create Date: 2026-03-04 10:00:00.000000

This migration adds:
- CHECK constraints for data integrity (price > 0, stock_quantity >= 0, quantity > 0)
- UNIQUE constraints to prevent duplicates (user_id, variant_id for cart items)
- Indexes for frequently queried fields for performance optimization
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '2b3c4d5e6f78'
down_revision: Union[str, None] = '18b397119ce8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add constraints and indexes for data integrity and performance."""
    
    # ========== CHECK CONSTRAINTS ==========
    
    # Product: price must be > 0
    op.create_check_constraint(  
        'ck_product_price_positive',
        'product',
        'price > 0'
    )
    
    # ProductVariant: stock_quantity must be >= 0
    op.create_check_constraint(
        'ck_productvariant_stock_nonnegative',
        'productvariant',
        'stock_quantity >= 0'
    )
    
    # ProductVariant: price_adjustment must be reasonable (base_price + adjustment > 0)
    # Note: We can't reference product.price here, so we set a reasonable range
    op.create_check_constraint(
        'ck_productvariant_price_adjustment',
        'productvariant',
        'price_adjustment > -1000000 AND price_adjustment < 1000000'
    )
    
    # Order: total_amount must be > 0
    op.create_check_constraint(
        'ck_order_total_positive',
        'order',
        'total_amount > 0'
    )
    
    # Order: status must be one of allowed values
    op.create_check_constraint(
        'ck_order_status_valid',
        'order',
        "status IN ('pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled')"
    )
    
    # OrderItem: quantity must be > 0
    op.create_check_constraint(
        'ck_orderitem_quantity_positive',
        'orderitem',
        'quantity > 0'
    )
    
    # OrderItem: price_at_purchase must be > 0
    op.create_check_constraint(
        'ck_orderitem_price_positive',
        'orderitem',
        'price_at_purchase > 0'
    )
    
    # CartItem: quantity must be > 0
    op.create_check_constraint(
        'ck_cartitem_quantity_positive',
        'cartitem',
        'quantity > 0'
    )
    
    # ========== UNIQUE CONSTRAINTS ==========
    
    # CartItem: prevent duplicate (cart_id, variant_id) pairs
    # First, we need to check if the column exists. This assumes variant_id was added in schema
    # If variant_id doesn't exist yet, this would fail. Let's use a try/catch approach in production
    # For now, assuming variant_id exists in CartItem model
    op.create_unique_constraint(
        'uq_cartitem_cart_variant',
        'cartitem',
        ['cart_id', 'variant_id']
    )
    
    # ========== PERFORMANCE INDEXES ==========
    
    # Order: index on (user_id, created_at DESC) for user order history
    op.create_index(
        'ix_order_user_created',
        'order',
        ['user_id', sa.text('created_at DESC')]
    )
    
    # CartItem: index on cart_id for cart queries
    op.create_index(
        'ix_cartitem_cart',
        'cartitem',
        ['cart_id']
    )
    
    # ProductVariant: index on (product_id, is_available) for filtering available variants
    op.create_index(
        'ix_productvariant_product_available',
        'productvariant',
        ['product_id', 'is_available']
    )
    
    # ProductImage: index on product_id for loading images
    op.create_index(
        'ix_productimage_product',
        'productimage',
        ['product_id']
    )
    
    # Order: index on status for filtering orders by status
    op.create_index(
        'ix_order_status',
        'order',
        ['status']
    )
    
    # Order: index on razorpay_order_id for payment lookups
    op.create_index(
        'ix_order_razorpay_order_id',
        'order',
        ['razorpay_order_id']
    )


def downgrade() -> None:
    """Remove constraints and indexes."""
    
    # Drop indexes
    op.drop_index('ix_order_razorpay_order_id', table_name='order')
    op.drop_index('ix_order_status', table_name='order')
    op.drop_index('ix_productimage_product', table_name='productimage')
    op.drop_index('ix_productvariant_product_available', table_name='productvariant')
    op.drop_index('ix_cartitem_cart', table_name='cartitem')
    op.drop_index('ix_order_user_created', table_name='order')
    
    # Drop unique constraints
    op.drop_constraint('uq_cartitem_cart_variant', 'cartitem', type_='unique')
    
    # Drop check constraints
    op.drop_constraint('ck_cartitem_quantity_positive', 'cartitem', type_='check')
    op.drop_constraint('ck_orderitem_price_positive', 'orderitem', type_='check')
    op.drop_constraint('ck_orderitem_quantity_positive', 'orderitem', type_='check')
    op.drop_constraint('ck_order_status_valid', 'order', type_='check')
    op.drop_constraint('ck_order_total_positive', 'order', type_='check')
    op.drop_constraint('ck_productvariant_price_adjustment', 'productvariant', type_='check')
    op.drop_constraint('ck_productvariant_stock_nonnegative', 'productvariant', type_='check')
    op.drop_constraint('ck_product_price_positive', 'product', type_='check')
