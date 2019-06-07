"""empty message

Revision ID: a36bb709b93d
Revises: 620cfca70dce
Create Date: 2019-06-07 18:35:35.289451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a36bb709b93d'
down_revision = '620cfca70dce'
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
