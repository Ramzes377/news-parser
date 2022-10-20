from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Article(db.Model):

    slug = db.Column(db.String(255), nullable=False, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    is_loaded = db.Column(db.Boolean, default=False)
    raw_html_preview = db.Column(db.Text, nullable=False)
    raw_html_content = db.Column(db.Text)
    raw_html_content_url = db.Column(db.Text, nullable=False)
    public_date = db.Column(db.DateTime)

    def __repr__(self):
        return f'{self.title}'


def get_articles():
    return db.session.query(Article).order_by(Article.public_date.desc())