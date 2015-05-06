"""empty message

Revision ID: 337aac9737d
Revises: None
Create Date: 2015-05-03 23:35:07.147459

"""

# revision identifiers, used by Alembic.
revision = '337aac9737d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=16), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tracklists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artisttags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tracks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('length', sa.Integer(), nullable=True),
    sa.Column('location', sa.UnicodeText(), nullable=True),
    sa.Column('name', sa.UnicodeText(), nullable=True),
    sa.Column('uuid', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('location'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('trackpositions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('track_id', sa.Integer(), nullable=True),
    sa.Column('tracklist_id', sa.Integer(), nullable=True),
    sa.CheckConstraint('position > -1'),
    sa.ForeignKeyConstraint(['track_id'], ['tracks.id'], ),
    sa.ForeignKeyConstraint(['tracklist_id'], ['tracklists.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('position', 'track_id', 'tracklist_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trackpositions')
    op.drop_table('tracks')
    op.drop_table('artisttags')
    op.drop_table('tracklists')
    op.drop_table('tags')
    op.drop_table('artists')
    ### end Alembic commands ###
