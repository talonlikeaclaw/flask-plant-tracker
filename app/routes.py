import os
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Plant, PlantImage, CareLog
from app.forms import LoginForm, RegistrationForm, PlantForm, CareLogForm

# Create blueprints
main_bp = Blueprint("main", __name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
plants_bp = Blueprint("plants", __name__, url_prefix="/plants")


def save_plant_image(plant, image_file, is_primary=False):
    """Save a plant image file to the filesystem and database"""
    # Get a secure filename and add timestamp to avoid duplicates
    filename = secure_filename(image_file.filename)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{filename}"

    # Create upload path if it doesn't exist yet
    upload_path = os.path.join(current_app.root_path, "static", "uploads", "plants")
    os.makedirs(upload_path, exist_ok=True)

    # Save the file
    image_file.save(os.path.join(upload_path, filename))

    # Create database record
    image = PlantImage(filename=filename, plant=plant, is_primary=is_primary)

    # If this is primary, ensure no other image is primary
    if is_primary:
        for img in plant.images:
            img.is_primary = False

    db.session.add(image)
    db.session.commit()
    return image
