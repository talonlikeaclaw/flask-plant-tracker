from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    SelectField,
    PasswordField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    NumberRange,
)


class LoginForm(FlaskForm):
    """Form for user login"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """Form for user registation"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=64)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")


class PlantForm(FlaskForm):
    """Form for adding/editing plants"""

    name = StringField("Plant Name", validators=[DataRequired(), Length(max=64)])
    species = StringField("Species", validators=[Length(max=120)])
    location = StringField("Location", validators=[Length(max=120)])
    watering_frequency = IntegerField(
        "Days Between Watering", validators=[DataRequired(), NumberRange(min=1, max=90)]
    )
    notes = TextAreaField("Notes", validators=[Optional()])
    image = FileField(
        "Plant Image",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png"], "Images only!")],
    )
    submit = SubmitField("Save Plant")
