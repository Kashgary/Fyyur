"""empty message

Revision ID: 52091c45015f
Revises: 1a41a50d7bed
Create Date: 2020-04-26 18:29:00.661968

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52091c45015f'
down_revision = '1a41a50d7bed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('id', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows', 'id')
    # ### end Alembic commands ###
