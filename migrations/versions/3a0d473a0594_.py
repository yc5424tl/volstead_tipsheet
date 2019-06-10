"""empty message

Revision ID: 3a0d473a0594
Revises: 2b750260af45
Create Date: 2019-06-10 07:14:08.396916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a0d473a0594'
down_revision = '2b750260af45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('first_last_uni_emp', 'employee', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('first_last_uni_emp', 'employee', ['first_name', 'last_name'])
    # ### end Alembic commands ###