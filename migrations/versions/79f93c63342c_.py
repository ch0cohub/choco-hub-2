"""empty message

Revision ID: 79f93c63342c
Revises: 16f3920c7e24
Create Date: 2024-11-11 11:41:47.273772

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '79f93c63342c'
down_revision = '16f3920c7e24'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('password',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('signupvalidation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('notepad')
    with op.batch_alter_table('data_set', schema=None) as batch_op:
        batch_op.add_column(sa.Column('num_features', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('num_products', sa.Integer(), nullable=False))

    with op.batch_alter_table('user_profile', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_verified', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_profile', schema=None) as batch_op:
        batch_op.drop_column('is_verified')

    with op.batch_alter_table('data_set', schema=None) as batch_op:
        batch_op.drop_column('num_products')
        batch_op.drop_column('num_features')

    op.create_table('notepad',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('title', mysql.VARCHAR(length=256), nullable=False),
    sa.Column('body', mysql.TEXT(), nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='notepad_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('signupvalidation')
    op.drop_table('password')
    # ### end Alembic commands ###
