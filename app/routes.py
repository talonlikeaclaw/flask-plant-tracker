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
from datetime import datetime
import os
from app import db
from app.models import User, Plant, PlantImage, CareLog
from app.forms import LoginForm, RegistrationForm, PlantForm, CareLogForm

# Create blueprints
main_bp = Blueprint("main", __name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
plants_bp = Blueprint("plants", __name__, url_prefix="/plants")
