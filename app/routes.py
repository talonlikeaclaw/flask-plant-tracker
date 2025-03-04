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


# Main routes
@main_bp.route("/")
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for("plants.list"))
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard with overview of plants needing care"""
    plants_need_water = current_user.plants.filter(Plant.needs_water == True).all()
    recent_care = (
        CareLog.query.join(Plant)
        .filter(Plant.user_id == current_user.id)
        .order_by(CareLog.timestamp.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "dashboard.html",
        plants_need_water=plants_need_water,
        recent_care=recent_care,
        now=datetime.utcnow(),
    )


# Authentication routes
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in to continue.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        next_page = request.args.get("next")
        if not next_page or not next_page.startswith("/"):
            next_page = url_for("main.dashboard")
        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for("main.index"))


# Plant routes
@plants_bp.route("/")
@login_required
def list():
    """List all plants"""
    plants = current_user.plants.all()
    return render_template("plants/list.html", plants=plants)


@plants_bp.route("<int:id>")
@login_required
def detail(id):
    """Show plant details"""
    plant = Plant.query.get_or_404(id)
    # Check if the plant belongs to the current user
    if plant.user_id != current_user.id:
        flash("You do not have permission to view this plant.", "danger")
        return redirect(url_for("plants.list"))

    care_logs = plant.care_logs.order_by(CareLog.timestamp.desc()).all()
    return render_template(
        "plants/detail.html", plant=plant, care_logs=care_logs, now=datetime.utcnow()
    )


@plants_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    """Add a new plant"""
    form = PlantForm()
    if form.validate_on_submit():
        plant = Plant(
            name=form.name.data,
            species=form.species.data,
            location=form.location.data,
            watering_frequency=form.watering_frequency.data,
            notes=form.notes.data,
            owner=current_user,
        )
        db.session.add(plant)
        db.session.commit()

        # Handle image upload if provided
        if form.image.data:
            save_plant_image(plant, form.image.data, is_primary=True)

        flash("Plant added successfully!", "success")
        return redirect(url_for("plants.detail", id=plant.id))

    return render_template("plants/form.html", form=form, title="Add New Plant")


@plants_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    """Edit an existing plant"""
    plant = Plant.query.get_or_404(id)
    # Verify ownership
    if plant.user_id != current_user.id:
        flash("You do not have permission to edit this plant.", "danger")
        return redirect(url_for("plants.list"))

    form = PlantForm(obj=plant)
    if form.validate_on_submit():
        form.populate_obj(plant)  # Update plant with form data
        db.session.commit()

        # Handle image upload if provided
        if form.image.data:
            save_plant_image(plant, form.image.data)

        flash("Plant updated successfully!", "success")
        return redirect(url_for("plants.detail", id=plant.id))

    return render_template("plants/form.html", form=form, title="Edit Plant")


@plants_bp.route("<int:id>/care", methods=["GET", "POST"])
@login_required
def add_care(id):
    """Record care for a plant"""
    plant = Plant.query.get_or_404(id)
    # Verify ownership
    if plant.user_id != current_user.id:
        flash("You do not have permission to record care for this plant.", "danger")
        return redirect(url_for("plants.list"))

    form = CareLogForm()
    if form.validate_on_submit():
        care_log = CareLog(
            care_type=form.care_type.data, notes=form.notes.data, plant=plant
        )

        # Update last_watered if this is a watering event
        if form.care_type.data == "watering":
            plant.last_watered = datetime.utcnow()

        # Update last_fertilized if this is a fertilizing event
        if form.care_type.data == "fertilizing":
            plant.last_fertilized = datetime.utcnow()

        db.session.add(care_log)
        db.session.commit()
        flash("Care recorded successfully!", "success")
        return redirect(url_for("plants.detail", id=plant.id))

    return render_template("plants/care_form.html", form=form, plant=plant)


@plants_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    """Delete a plant"""
    plant = Plant.query.get_or_404(id)
    # Verify ownership
    if plant.user_id != current_user.id:
        flash("You do not have permission to delete this plant.", "danger")
        return redirect(url_for("plants.list"))

    db.session.delete(plant)
    db.session.commit()
    flash("Plant deleted successfully!", "success")
    return redirect(url_for("plants.list"))
