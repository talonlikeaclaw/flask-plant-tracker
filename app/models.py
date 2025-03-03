from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    """Represents a User object"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    plants = db.relationship("Plant", backref="owner", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Plant(db.Model):
    """Represents a Plant object"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    species = db.Column(db.String(120))
    date_acquired = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(120))
    watering_frequency = db.Column(db.Integer)
    last_watered = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    care_logs = db.relationship("CareLog", backref="plant", lazy="dynamic")

    def __repr__(self):
        return f"<Plant {self.name}>"

    def needs_water(self):
        """Checks if plant needs watering based on frequency"""
        if not self.last_watered:
            return True
        days_since = (datetime.utcnow() - self.last_watered).days
        return days_since >= self.watering_frequency
