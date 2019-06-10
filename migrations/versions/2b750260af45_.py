"""empty message

Revision ID: 2b750260af45
Revises: 
Create Date: 2019-06-10 07:13:36.915463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b750260af45'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('first_last_uni_emp', 'employee', ['first_name', 'last_name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('first_last_uni_emp', 'employee', type_='unique')
    # ### end Alembic commands ###
