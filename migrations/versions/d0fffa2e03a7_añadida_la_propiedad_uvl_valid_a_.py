"""Añadida la propiedad uvl_valid   a FeatureModel

Revision ID: d0fffa2e03a7
Revises: d20659253c46
Create Date: 2024-11-29 22:55:50.403153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0fffa2e03a7'
down_revision = 'd20659253c46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feature_model', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uvl_valid', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feature_model', schema=None) as batch_op:
        batch_op.drop_column('uvl_valid')

    # ### end Alembic commands ###
