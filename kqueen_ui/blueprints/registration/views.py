from flask import Blueprint, current_app as app, flash, redirect, render_template, url_for
from flask_mail import Mail, Message
from kqueen_ui.api import get_service_client
from slugify import slugify

from .forms import UserRegistrationForm
from .utils import confirm_token, generate_confirmation_token

import logging

logger = logging.getLogger(__name__)
mail = Mail()

registration = Blueprint('registration', __name__, template_folder='templates')


@registration.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        client = get_service_client()

        try:
            organization = {
                'name': form.organization_name.data,
                'namespace': slugify(form.organization_name.data)
            }
            response = client.organization.create(organization)

            if response.status > 200:
                flash('Could not create organization.', 'danger')
                return render_template('registration/register.html', form=form)

            organization_id = response.data['id']
        except Exception as e:
            logger.error('register view: {}'.format(repr(e)))
            flash('Could not create organization.', 'danger')
            return render_template('registration/register.html', form=form)

        try:
            organization_ref = 'Organization:{}'.format(organization_id)
            user = {
                'username': form.username.data,
                'password': form.password_1.data,
                'email': form.email.data,
                'organization': organization_ref,
                'active': False
            }
            response = client.user.create(user)

            if response.status > 200:
                flash('Could not create user.', 'danger')
                client.organization.delete(organization_id)
                return render_template('registration/register.html', form=form)
        except Exception as e:
            logger.error('register view: {}'.format(repr(e)))
            client.organization.delete(organization_id)
            flash('Could not create user.', 'danger')
            return render_template('registration/register.html', form=form)

        flash('Registration successful. Check your e-mail for the activation link!', 'success')

        # Init mail handler
        mail.init_app(app)
        token = generate_confirmation_token(user['email'])
        html = render_template('registration/email/verify_email.html', token=token)
        msg = Message(
            '[KQueen] E-mail verification',
            recipients=[user['email']],
            html=html
        )
        try:
            mail.send(msg)
        except Exception as e:
            logger.error('register view: {}'.format(repr(e)))
            flash('Could not send verification e-mail, please try again later.', 'danger')
            return render_template('registration/register.html', form=form)

        return redirect(url_for('ui.login'))

    return render_template('registration/register.html', form=form)


@registration.route('/verify/<token>')
def verify_email(token):
    email = confirm_token(token)
    if not email:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('ui.index'))

    client = get_service_client()
    _users = client.user.list()
    users = _users.data

    # TODO: this logic realies heavily on unique emails, this is not the case on backend right now
    filtered = [u for u in users if u.get('email', None) == email]
    if filtered:
        user = filtered[0]
        if user.get('active', None):
            flash('Account already verified. Please login.', 'success')
        else:
            user['active'] = True
            client.user.update(user['id'], user)
            flash('You have confirmed your account. Thanks!', 'success')
    else:
        flash('No user found based on given e-mail.', 'danger')
    return redirect(url_for('ui.index'))
