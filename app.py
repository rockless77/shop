import os
import uuid
from werkzeug.utils import secure_filename
from flask import (
    Flask, render_template, request, redirect, 
    url_for, session, flash, send_from_directory,
    jsonify
)
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import (
    LoginManager, UserMixin, login_user, 
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime, timedelta
from sqlalchemy import or_
from flask_apscheduler import APScheduler

# ─── App & Extensions ────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Upload configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db      = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

@socketio.on('join_auction')
def handle_join_auction(data):
    product_id = data.get('product_id')
    if product_id:
        room = f'auction_{product_id}'
        join_room(room)

@socketio.on('leave_auction')
def handle_leave_auction(data):
    product_id = data.get('product_id')
    if product_id:
        room = f'auction_{product_id}'
        leave_room(room)

@app.route('/api/auction/<int:product_id>/time')
def get_auction_time(product_id):
    product = Product.query.get_or_404(product_id)
    if product.auction_end:
        time_left = (product.auction_end - datetime.utcnow()).total_seconds()
        return jsonify({'time_left': max(0, time_left)})
    return jsonify({'time_left': None})

# ─── Models ───────────────────────────────────────────────────────────────────────

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # Authentication
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile Information
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    bio = db.Column(db.String(500))
    profile_image = db.Column(db.String(255), default='default_profile.jpg')
    
    # Display Preferences
    theme = db.Column(db.String(50), default='light')  # light, dark, system
    language = db.Column(db.String(10), default='en')
    timezone = db.Column(db.String(50), default='UTC')
    items_per_page = db.Column(db.Integer, default=10)
    
    # Notification Preferences
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    marketing_emails = db.Column(db.Boolean, default=False)
    
    # Notification Types
    bid_notifications = db.Column(db.Boolean, default=True)
    auction_end_notifications = db.Column(db.Boolean, default=True)
    order_update_notifications = db.Column(db.Boolean, default=True)
    price_drop_notifications = db.Column(db.Boolean, default=True)
    new_listing_notifications = db.Column(db.Boolean, default=True)
    
    # Email Preferences
    email_frequency = db.Column(db.String(20), default='daily')  # immediate, daily, weekly
    
    # Privacy Preferences
    profile_visibility = db.Column(db.String(20), default='public')  # public, registered, private
    activity_visibility = db.Column(db.String(20), default='public')  # public, registered, private
    show_email = db.Column(db.Boolean, default=False)
    show_phone = db.Column(db.Boolean, default=False)
    show_full_name = db.Column(db.Boolean, default=False)
    show_bid_activity = db.Column(db.Boolean, default=False)
    show_won_auctions = db.Column(db.Boolean, default=False)
    
    # Account Information
    default_address = db.Column(db.String(500))
    default_city = db.Column(db.String(100))
    default_state = db.Column(db.String(100))
    default_zip = db.Column(db.String(20))
    default_country = db.Column(db.String(100), default='United States')
    default_payment_method = db.Column(db.String(100))
    default_currency = db.Column(db.String(3), default='USD')
    
    # Security
    two_factor_enabled = db.Column(db.Boolean, default=False)
    last_password_change = db.Column(db.DateTime, default=db.func.now())
    account_created = db.Column(db.DateTime, default=db.func.now())
    last_login = db.Column(db.DateTime, default=db.func.now())
    
    # Shipping Preferences
    preferred_shipping_method = db.Column(db.String(20), default='standard')  # standard, express, overnight
    shipping_notifications = db.Column(db.Boolean, default=True)
    signature_required = db.Column(db.Boolean, default=False)
    show_delivery_instructions = db.Column(db.Boolean, default=True)
    
    # Account Recovery
    recovery_email = db.Column(db.String(150))
    recovery_phone = db.Column(db.String(20))
    security_question1 = db.Column(db.String(50))
    security_answer1 = db.Column(db.String(100))
    security_question2 = db.Column(db.String(50))
    security_answer2 = db.Column(db.String(100))
    
    # Relationships
    products = db.relationship('Product', back_populates='seller', lazy=True)
    cart_items = db.relationship('Cart', backref='user', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    user_bids = db.relationship('Bid', backref='bidder', foreign_keys='Bid.user_id', lazy=True)
    # Direct relationship without backref
    tickets = db.relationship('SupportTicket', foreign_keys='SupportTicket.user_id', lazy=True)
    
    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)
        self.last_password_change = datetime.utcnow()

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)
        
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
        
    def get_address(self):
        if all([self.default_address, self.default_city, self.default_state, self.default_zip]):
            return f"{self.default_address}, {self.default_city}, {self.default_state} {self.default_zip}, {self.default_country}"
        return None


class ProductImage(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    filename   = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class Product(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.String(500), nullable=True)
    price         = db.Column(db.Float, nullable=False)
    
    # Auction fields
    is_auction    = db.Column(db.Boolean, default=False)
    start_price   = db.Column(db.Float, nullable=True)
    current_bid   = db.Column(db.Float, nullable=True)
    min_increment = db.Column(db.Float, default=1.0)  # Minimum bid increment
    auction_end   = db.Column(db.DateTime, nullable=True)
    status        = db.Column(db.String(20), default='active')  # active, sold, expired
    
    # Image relationship
    images        = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    
    seller_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller        = db.relationship('User', back_populates='products')
    bids          = db.relationship('Bid', back_populates='product', lazy=True, order_by='Bid.amount.desc()')
    order_items   = db.relationship('OrderItem', backref='product', lazy=True)
    
    @property
    def time_left(self):
        if not self.is_auction or not self.auction_end:
            return None
        return self.auction_end - datetime.utcnow()
    
    @property
    def highest_bidder(self):
        if not self.bids:
            return None
        return self.bids[0].bidder

class Bid(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    amount      = db.Column(db.Float, nullable=False)
    created_at  = db.Column(db.DateTime, default=db.func.now())
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id  = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # Relationships
    product = db.relationship('Product', back_populates='bids')

class Cart(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)            # ← new field


class Wishlist(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),    nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


class Order(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status          = db.Column(db.String(50), default='Processing')
    created_at      = db.Column(db.DateTime, default=db.func.now())

    shipping_name   = db.Column(db.String(200), nullable=False)
    shipping_addr   = db.Column(db.String(500), nullable=False)
    payment_method  = db.Column(db.String(100), nullable=False)

    total_price     = db.Column(db.Float, nullable=False)   # ← new
    tracking_number = db.Column(db.String(64), unique=True, nullable=True)
    items           = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)


class PaymentMethod(db.Model):
    __tablename__ = 'payment_method'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)  # credit_card, paypal, bank_account, etc.
    is_default = db.Column(db.Boolean, default=False)
    nickname = db.Column(db.String(100))
    last_four = db.Column(db.String(4))  # Last 4 digits of card or account
    expiry_month = db.Column(db.Integer)  # For credit cards
    expiry_year = db.Column(db.Integer)  # For credit cards
    card_brand = db.Column(db.String(20))  # visa, mastercard, etc.
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # Relationship with User
    user = db.relationship('User', backref='payment_methods')


class ShippingAddress(db.Model):
    __tablename__ = 'shipping_address'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nickname = db.Column(db.String(100))  # e.g., Home, Work, etc.
    recipient_name = db.Column(db.String(100), nullable=False)
    street_address1 = db.Column(db.String(100), nullable=False)
    street_address2 = db.Column(db.String(100))
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # Relationship with User
    user = db.relationship('User', backref='shipping_addresses')


class LoginHistory(db.Model):
    __tablename__ = 'login_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=db.func.now())
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))  # Browser/device info
    location = db.Column(db.String(100))    # Approximate location based on IP
    success = db.Column(db.Boolean, default=True)  # Whether login was successful
    
    # Relationship with User
    user = db.relationship('User', backref='login_history')

class SupportTicket(db.Model):
    __tablename__ = 'support_ticket'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open', nullable=False)  # open, in_progress, resolved, closed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # Direct relationship without backref
    creator = db.relationship('User', foreign_keys=[user_id], lazy=True)
    
    def __repr__(self):
        return f'<SupportTicket {self.id} - {self.subject}>'           # ← new


# ─── Flask-Login Loader ─────────────────────────────────────────────────────────

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Public Routes ───────────────────────────────────────────────────────────────

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/my_listings')
@login_required
def my_listings():
    # Grab only the products this user has created
    products = Product.query.filter_by(seller_id=current_user.id).all()
    return render_template('my_listings.html', products=products)

@app.route('/profile')
@login_required
def profile():
    # Get user's won auctions (highest bid is theirs and auction is ended)
    won_auctions = Product.query.join(Bid).filter(
        Product.is_auction == True,
        Product.status.in_(['sold', 'expired']),
        Bid.user_id == current_user.id,
        Bid.amount == Product.current_bid
    ).all()
    
    # Get active bids (auctions where user has placed a bid and auction is still active)
    active_bids = db.session.query(Product, Bid.amount).join(Bid).filter(
        Product.is_auction == True,
        Product.status == 'active',
        Bid.user_id == current_user.id
    ).order_by(Bid.amount.desc()).all()
    
    return render_template('profile.html', 
                          user=current_user, 
                          won_auctions=won_auctions, 
                          active_bids=active_bids)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)

@app.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile_settings():
    if request.method == 'POST':
        # Update personal information
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.phone_number = request.form.get('phone_number')
        current_user.bio = request.form.get('bio')
        
        # Handle profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                # Generate secure filename
                filename = secure_filename(file.filename)
                # Append timestamp to prevent duplicate filenames
                filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                # Save the file
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', filename))
                current_user.profile_image = filename
        
        # Update theme and language preferences
        current_user.theme = request.form.get('theme')
        current_user.language = request.form.get('language')
        current_user.timezone = request.form.get('timezone')
        
        # Save changes
        db.session.commit()
        flash('Profile settings updated successfully!', 'success')
        return redirect(url_for('profile_settings'))
    
    return render_template('settings_profile.html', user=current_user)

@app.route('/settings/notifications', methods=['GET', 'POST'])
@login_required
def notification_settings():
    if request.method == 'POST':
        # Update notification settings
        current_user.email_notifications = 'email_notifications' in request.form
        current_user.push_notifications = 'push_notifications' in request.form
        current_user.sms_notifications = 'sms_notifications' in request.form
        
        # Update notification types
        current_user.bid_notifications = 'bid_notifications' in request.form
        current_user.auction_end_notifications = 'auction_end_notifications' in request.form
        current_user.order_update_notifications = 'order_update_notifications' in request.form
        current_user.price_drop_notifications = 'price_drop_notifications' in request.form
        current_user.new_listing_notifications = 'new_listing_notifications' in request.form
        
        # Update email preferences
        current_user.marketing_emails = 'marketing_emails' in request.form
        current_user.email_frequency = request.form.get('email_frequency', 'daily')
        
        # Save changes
        db.session.commit()
        flash('Notification settings updated successfully!', 'success')
        return redirect(url_for('notification_settings'))
    
    return render_template('settings_notifications.html', user=current_user)

@app.route('/settings/privacy', methods=['GET', 'POST'])
@login_required
def privacy_settings():
    if request.method == 'POST':
        # Update personal information visibility
        current_user.show_email = 'show_email' in request.form
        current_user.show_phone = 'show_phone' in request.form
        current_user.show_full_name = 'show_full_name' in request.form
        
        # Update profile and activity visibility
        current_user.profile_visibility = request.form.get('profile_visibility', 'public')
        current_user.activity_visibility = request.form.get('activity_visibility', 'public')
        
        # Update activity privacy settings
        current_user.show_bid_activity = 'show_bid_activity' in request.form
        current_user.show_won_auctions = 'show_won_auctions' in request.form
        
        db.session.commit()
        flash('Privacy settings updated successfully!', 'success')
        return redirect(url_for('privacy_settings'))
    
    return render_template('settings_privacy.html', user=current_user)

@app.route('/settings/display', methods=['GET', 'POST'])
@login_required
def display_settings():
    if request.method == 'POST':
        # Update theme and appearance settings
        current_user.theme = request.form.get('theme', 'light')
        
        # Update language and localization settings
        current_user.language = request.form.get('language', 'en')
        current_user.timezone = request.form.get('timezone', 'UTC')
        
        # Update display preferences
        current_user.items_per_page = int(request.form.get('items_per_page', 10))
        current_user.default_currency = request.form.get('default_currency', 'USD')
        
        # Save changes
        db.session.commit()
        flash('Display settings updated successfully!', 'success')
        return redirect(url_for('display_settings'))
    
    return render_template('settings_display.html', user=current_user)

@app.route('/settings/address', methods=['GET', 'POST'])
@login_required
def address_settings():
    if request.method == 'POST':
        # Update address settings
        current_user.default_address = request.form.get('address')
        current_user.default_city = request.form.get('city')
        current_user.default_state = request.form.get('state')
        current_user.default_zip = request.form.get('zip')
        current_user.default_country = request.form.get('country')
        
        # Update shipping preferences
        current_user.preferred_shipping_method = request.form.get('preferred_shipping_method', 'standard')
        current_user.shipping_notifications = 'shipping_notifications' in request.form
        current_user.signature_required = 'signature_required' in request.form
        current_user.show_delivery_instructions = 'show_delivery_instructions' in request.form
        
        db.session.commit()
        flash('Address settings updated successfully!', 'success')
        return redirect(url_for('address_settings'))
    
    # Get user's saved shipping addresses
    shipping_addresses = ShippingAddress.query.filter_by(user_id=current_user.id).all()
    
    return render_template('settings_address.html', user=current_user, shipping_addresses=shipping_addresses)


@app.route('/settings/address/add', methods=['GET', 'POST'])
@login_required
def add_address():
    if request.method == 'POST':
        # Create new shipping address
        new_address = ShippingAddress(
            user_id=current_user.id,
            nickname=request.form.get('nickname'),
            recipient_name=request.form.get('recipient_name'),
            street_address1=request.form.get('street_address1'),
            street_address2=request.form.get('street_address2'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            postal_code=request.form.get('postal_code'),
            country=request.form.get('country'),
            phone_number=request.form.get('phone_number'),
            is_default=request.form.get('is_default') == 'on'
        )
        
        # If this is set as default, unset any other default addresses
        if new_address.is_default:
            ShippingAddress.query.filter_by(user_id=current_user.id, is_default=True).update({ShippingAddress.is_default: False})
        
        db.session.add(new_address)
        db.session.commit()
        
        flash('Shipping address added successfully!', 'success')
        return redirect(url_for('address_settings'))
    
    return render_template('add_address.html')


@app.route('/settings/address/edit/<int:address_id>', methods=['GET', 'POST'])
@login_required
def edit_address(address_id):
    # Get the shipping address
    address = ShippingAddress.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        # Update shipping address
        address.nickname = request.form.get('nickname')
        address.recipient_name = request.form.get('recipient_name')
        address.street_address1 = request.form.get('street_address1')
        address.street_address2 = request.form.get('street_address2')
        address.city = request.form.get('city')
        address.state = request.form.get('state')
        address.postal_code = request.form.get('postal_code')
        address.country = request.form.get('country')
        address.phone_number = request.form.get('phone_number')
        address.is_default = request.form.get('is_default') == 'on'
        
        # If this is set as default, unset any other default addresses
        if address.is_default:
            ShippingAddress.query.filter(ShippingAddress.user_id == current_user.id, 
                                       ShippingAddress.id != address.id, 
                                       ShippingAddress.is_default == True).update({ShippingAddress.is_default: False})
        
        db.session.commit()
        flash('Shipping address updated successfully!', 'success')
        return redirect(url_for('address_settings'))
    
    return render_template('edit_address.html', address=address)


@app.route('/settings/address/delete/<int:address_id>')
@login_required
def delete_address(address_id):
    # Get the shipping address
    address = ShippingAddress.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    
    # Check if it's the default address
    was_default = address.is_default
    
    # Delete the shipping address
    db.session.delete(address)
    
    # If it was the default address, set another one as default if available
    if was_default:
        new_default = ShippingAddress.query.filter_by(user_id=current_user.id).first()
        if new_default:
            new_default.is_default = True
    
    db.session.commit()
    flash('Shipping address deleted successfully!', 'success')
    return redirect(url_for('address_settings'))


@app.route('/settings/address/set-default/<int:address_id>')
@login_required
def set_default_address(address_id):
    # Get the shipping address
    address = ShippingAddress.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    
    # Unset any other default addresses
    ShippingAddress.query.filter_by(user_id=current_user.id, is_default=True).update({ShippingAddress.is_default: False})
    
    # Set this address as default
    address.is_default = True
    db.session.commit()
    
    flash('Default shipping address updated successfully!', 'success')
    return redirect(url_for('address_settings'))

@app.route('/settings/payment', methods=['GET', 'POST'])
@login_required
def payment_settings():
    if request.method == 'POST':
        # Update payment settings
        current_user.default_payment_method = request.form.get('payment_method')
        current_user.default_currency = request.form.get('currency')
        
        db.session.commit()
        flash('Payment settings updated successfully!', 'success')
        return redirect(url_for('payment_settings'))
    
    # Get user's saved payment methods
    payment_methods = PaymentMethod.query.filter_by(user_id=current_user.id).all()
    
    return render_template('settings_payment.html', user=current_user, payment_methods=payment_methods)


@app.route('/settings/payment/add/<type>', methods=['GET', 'POST'])
@login_required
def add_payment_method(type):
    if type not in ['credit_card', 'paypal', 'bank_transfer']:
        flash('Invalid payment method type.', 'danger')
        return redirect(url_for('payment_settings'))
    
    if request.method == 'POST':
        # Create new payment method
        new_method = PaymentMethod(
            user_id=current_user.id,
            payment_type=type,
            nickname=request.form.get('nickname'),
            is_default=request.form.get('is_default') == 'on'
        )
        
        if type == 'credit_card':
            # Validate and save credit card info
            new_method.card_brand = request.form.get('card_brand')
            new_method.last_four = request.form.get('card_number')[-4:] if request.form.get('card_number') else ''
            new_method.expiry_month = request.form.get('expiry_month')
            new_method.expiry_year = request.form.get('expiry_year')
        elif type == 'bank_transfer':
            # Save bank account info
            new_method.last_four = request.form.get('account_number')[-4:] if request.form.get('account_number') else ''
        
        # If this is set as default, unset any other default methods
        if new_method.is_default:
            PaymentMethod.query.filter_by(user_id=current_user.id, is_default=True).update({PaymentMethod.is_default: False})
        
        db.session.add(new_method)
        db.session.commit()
        
        flash('Payment method added successfully!', 'success')
        return redirect(url_for('payment_settings'))
    
    return render_template('add_payment_method.html', type=type)


@app.route('/settings/payment/edit/<int:method_id>', methods=['GET', 'POST'])
@login_required
def edit_payment_method(method_id):
    # Get the payment method
    method = PaymentMethod.query.filter_by(id=method_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        # Update payment method
        method.nickname = request.form.get('nickname')
        method.is_default = request.form.get('is_default') == 'on'
        
        if method.payment_type == 'credit_card':
            # Update credit card info
            method.expiry_month = request.form.get('expiry_month')
            method.expiry_year = request.form.get('expiry_year')
        
        # If this is set as default, unset any other default methods
        if method.is_default:
            PaymentMethod.query.filter(PaymentMethod.user_id == current_user.id, 
                                      PaymentMethod.id != method.id, 
                                      PaymentMethod.is_default == True).update({PaymentMethod.is_default: False})
        
        db.session.commit()
        flash('Payment method updated successfully!', 'success')
        return redirect(url_for('payment_settings'))
    
    return render_template('edit_payment_method.html', method=method)


@app.route('/settings/payment/delete/<int:method_id>')
@login_required
def delete_payment_method(method_id):
    # Get the payment method
    method = PaymentMethod.query.filter_by(id=method_id, user_id=current_user.id).first_or_404()
    
    # Check if it's the default method
    was_default = method.is_default
    
    # Delete the payment method
    db.session.delete(method)
    
    # If it was the default method, set another one as default if available
    if was_default:
        new_default = PaymentMethod.query.filter_by(user_id=current_user.id).first()
        if new_default:
            new_default.is_default = True
    
    db.session.commit()
    flash('Payment method deleted successfully!', 'success')
    return redirect(url_for('payment_settings'))


@app.route('/settings/payment/set-default/<int:method_id>')
@login_required
def set_default_payment_method(method_id):
    # Get the payment method
    method = PaymentMethod.query.filter_by(id=method_id, user_id=current_user.id).first_or_404()
    
    # Unset any other default methods
    PaymentMethod.query.filter_by(user_id=current_user.id, is_default=True).update({PaymentMethod.is_default: False})
    
    # Set this method as default
    method.is_default = True
    db.session.commit()
    
    flash('Default payment method updated successfully!', 'success')
    return redirect(url_for('payment_settings'))
@app.route('/settings/security', methods=['GET', 'POST'])
@login_required
def security_settings():
    if request.method == 'POST':
        # Handle password change
        if 'update_password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate current password
            if not check_password_hash(current_user.password_hash, current_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('security_settings'))
            
            # Validate new password
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('security_settings'))
            
            if len(new_password) < 8:
                flash('Password must be at least 8 characters long.', 'danger')
                return redirect(url_for('security_settings'))
            
            # Update password
            current_user.password_hash = generate_password_hash(new_password)
            current_user.last_password_change = datetime.now()
            db.session.commit()
            
            flash('Password updated successfully!', 'success')
            return redirect(url_for('security_settings'))
        
        # Handle two-factor authentication toggle
        current_user.two_factor_enabled = 'two_factor_enabled' in request.form
        
        # Handle recovery email update
        if 'update_recovery_email' in request.form:
            recovery_email = request.form.get('recovery_email')
            if recovery_email and recovery_email != current_user.email:  # Ensure recovery email is different from primary
                current_user.recovery_email = recovery_email
                flash('Recovery email updated successfully!', 'success')
            elif recovery_email == current_user.email:
                flash('Recovery email must be different from your primary email.', 'warning')
        
        # Handle recovery phone update
        if 'update_recovery_phone' in request.form:
            recovery_phone = request.form.get('recovery_phone')
            if recovery_phone:
                current_user.recovery_phone = recovery_phone
                flash('Recovery phone updated successfully!', 'success')
        
        # Handle security questions update
        if 'update_security_questions' in request.form:
            security_question1 = request.form.get('security_question1')
            security_answer1 = request.form.get('security_answer1')
            security_question2 = request.form.get('security_question2')
            security_answer2 = request.form.get('security_answer2')
            
            # Only update if both questions are selected and answers provided
            if security_question1 and security_question2 and security_answer1 and security_answer2:
                # Don't update if answer field contains the masked value
                if security_answer1 != '********':
                    current_user.security_question1 = security_question1
                    current_user.security_answer1 = security_answer1
                
                if security_answer2 != '********':
                    current_user.security_question2 = security_question2
                    current_user.security_answer2 = security_answer2
                
                flash('Security questions updated successfully!', 'success')
            else:
                flash('Please select both security questions and provide answers.', 'warning')
        
        db.session.commit()
        return redirect(url_for('security_settings'))
    
    # Get recent login history (last 5 entries)
    login_history = LoginHistory.query.filter_by(user_id=current_user.id).order_by(LoginHistory.login_time.desc()).limit(5).all()
    
    return render_template('settings_security.html', user=current_user, login_history=login_history)


@app.route('/settings/security/login-history')
@login_required
def view_full_login_history():
    # Get full login history
    login_history = LoginHistory.query.filter_by(user_id=current_user.id).order_by(LoginHistory.login_time.desc()).all()
    
    return render_template('login_history.html', user=current_user, login_history=login_history)


@app.route('/orders')
@login_required
def order_history():
    # Get all orders for the current user
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    # Get the specific order and verify it belongs to the current user
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    # Get all items in this order with product details
    order_items = db.session.query(OrderItem, Product).join(Product).filter(OrderItem.order_id == order_id).all()
    
    return render_template('order_detail.html', order=order, order_items=order_items)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # Get IP address and user agent
        ip_address = request.remote_addr
        user_agent = request.user_agent.string
        location = 'Unknown'  # In a real app, you might use a geolocation service
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.now()
            
            # Record successful login
            login_record = LoginHistory(
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                location=location,
                success=True
            )
            db.session.add(login_record)
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            # Record failed login attempt if user exists
            if user:
                login_record = LoginHistory(
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    location=location,
                    success=False
                )
                db.session.add(login_record)
                db.session.commit()
            
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        u = request.form['username']
        e = request.form['email']
        p = request.form['password']
        user = User(username=u, email=e)
        user.set_password(p)
        db.session.add(user); db.session.commit()
        flash('Registered! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    # Verify password
    password = request.form.get('password')
    if not check_password_hash(current_user.password_hash, password):
        flash('Incorrect password. Account deletion canceled.', 'danger')
        return redirect(url_for('privacy_settings'))
    
    # Get user ID before logging out
    user_id = current_user.id
    
    # Log the user out
    logout_user()
    
    # Delete all related data
    # 1. Delete login history
    LoginHistory.query.filter_by(user_id=user_id).delete()
    
    # 2. Delete payment methods
    PaymentMethod.query.filter_by(user_id=user_id).delete()
    
    # 3. Delete shipping addresses
    ShippingAddress.query.filter_by(user_id=user_id).delete()
    
    # 4. Delete support tickets
    SupportTicket.query.filter_by(user_id=user_id).delete()
    
    # 5. Delete bids
    Bid.query.filter_by(user_id=user_id).delete()
    
    # 6. Delete cart items
    Cart.query.filter_by(user_id=user_id).delete()
    
    # 7. Delete orders
    # First get all orders by this user
    user_orders = Order.query.filter_by(user_id=user_id).all()
    for order in user_orders:
        # Delete order items for each order
        OrderItem.query.filter_by(order_id=order.id).delete()
    # Then delete the orders
    Order.query.filter_by(user_id=user_id).delete()
    
    # 8. Handle products - mark as deleted or reassign
    # For simplicity, we'll just delete them here
    # In a real app, you might want to handle this differently
    Product.query.filter_by(seller_id=user_id).delete()
    
    # 9. Finally, delete the user
    User.query.filter_by(id=user_id).delete()
    
    # Commit all changes
    db.session.commit()
    
    flash('Your account has been permanently deleted.', 'success')
    return redirect(url_for('index'))


@app.route('/order/<int:oid>/update', methods=['POST'])
@login_required
def update_order(oid):
    # ideally check current_user.is_admin
    o = Order.query.get_or_404(oid)

    # Update status if provided
    if 'status' in request.form:
        o.status = request.form['status']

    # **New**: capture seller-entered tracking number
    tracking = request.form.get('tracking_number', '').strip()
    if tracking:
        o.tracking_number = tracking

    db.session.commit()
    flash(f'Order #{oid} updated.', 'success')
    return redirect(url_for('my_sales'))   # or whatever your seller view is




# ─── Auction Processing ─────────────────────────────────────────────────────────

@scheduler.task("interval", id="process_auctions", seconds=60, misfire_grace_time=900)
def process_ended_auctions():
    """Check for auctions that have ended and update their status."""
    now = datetime.utcnow()
    
    # Find active auctions that have ended
    ended_auctions = Product.query.filter(
        Product.is_auction == True,
        Product.status == 'active',
        Product.auction_end <= now
    ).all()
    
    for auction in ended_auctions:
        if auction.bids:  # Auction received bids
            # Mark as sold to highest bidder
            auction.status = 'sold'
            
            # Create order for the winning bidder
            winning_bid = auction.bids[0]  # First bid is highest due to our ordering
            
            order = Order(
                user_id=winning_bid.user_id,
                status='Awaiting Payment',
                shipping_name=winning_bid.user.username,  # In a real app, get this from a form
                shipping_addr="To be provided",  # In a real app, get this from a form
                payment_method="To be provided",  # In a real app, get this from a form
                total_price=winning_bid.amount
            )
            
            # Add the auction item to the order
            order_item = OrderItem(
                order=order,
                product_id=auction.id,
                quantity=1
            )
            
            db.session.add(order)
            db.session.add(order_item)
        else:  # No bids placed
            auction.status = 'expired'
    
    db.session.commit()
    print(f"Processed {len(ended_auctions)} ended auctions")


# ─── Auction Routes ───────────────────────────────────────────────────────────

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, product_id):
    if file and allowed_file(file.filename):
        # Create a unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{product_id}_{uuid.uuid4().hex[:8]}.{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/auction/create', methods=['GET', 'POST'])
@login_required
def create_auction():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_price = float(request.form['start_price'])
        min_increment = float(request.form.get('min_increment', 1.0))
        duration_days = int(request.form.get('duration_days', 7))
        
        auction_end = datetime.utcnow() + timedelta(days=duration_days)
        
        product = Product(
            name=name,
            description=description,
            price=start_price,  # Initial price
            is_auction=True,
            start_price=start_price,
            current_bid=start_price,
            min_increment=min_increment,
            auction_end=auction_end,
            seller_id=current_user.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Handle image uploads
        files = request.files.getlist('images')
        is_primary = True  # First image will be primary
        
        for file in files:
            if file.filename:
                filename = save_uploaded_file(file, product.id)
                if filename:
                    image = ProductImage(
                        filename=filename,
                        product_id=product.id,
                        is_primary=is_primary
                    )
                    db.session.add(image)
                    is_primary = False  # Subsequent images are not primary
        
        db.session.commit()
        
        flash('Auction created successfully!', 'success')
        return redirect(url_for('view_auction', product_id=product.id))
    
    return render_template('create_auction.html')

@app.route('/auction/<int:product_id>')
def view_auction(product_id):
    product = Product.query.get_or_404(product_id)
    if not product.is_auction:
        return redirect(url_for('product', product_id=product_id))
    
    return render_template('view_auction.html', product=product)

@app.route('/place_bid/<int:product_id>', methods=['POST'])
@login_required
def place_bid(product_id):
    product = Product.query.get_or_404(product_id)
    
    try:
        bid_amount = float(request.form['bid_amount'])
    except (ValueError, KeyError):
        flash('Invalid bid amount', 'error')
        return redirect(url_for('view_auction', product_id=product_id))

    # Check if auction is still active
    if product.status != 'active':
        flash('This auction has ended.', 'error')
        return redirect(url_for('view_auction', product_id=product_id))

    # Check if user is not the seller
    if current_user.id == product.seller_id:
        flash('You cannot bid on your own auction.', 'error')
        return redirect(url_for('view_auction', product_id=product_id))

    # Check if bid is high enough
    min_bid = (product.current_bid or product.start_price) + product.min_increment
    if bid_amount < min_bid:
        flash(f'Bid must be at least ${min_bid:.2f}', 'error')
        return redirect(url_for('view_auction', product_id=product_id))
    
    try:
        # Create and save the bid
        bid = Bid(amount=bid_amount, product_id=product_id, user_id=current_user.id)
        product.current_bid = bid_amount
        db.session.add(bid)
        db.session.commit()

        # Emit bid update to all clients in the auction room
        socketio.emit('bid_update', {
            'product_id': product_id,
            'current_bid': bid_amount,
            'user_name': current_user.username,
            'bid_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'bid_count': len(product.bids)
        }, room=f'auction_{product_id}')

        flash('Your bid has been placed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while placing your bid. Please try again.', 'error')

    return redirect(url_for('view_auction', product_id=product_id))

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_auction')
def handle_join_auction(data):
    room = f'auction_{data["product_id"]}'
    join_room(room)
    print(f'Client joined auction room: {room}')

@socketio.on('leave_auction')
def handle_leave_auction(data):
    room = f'auction_{data["product_id"]}'
    leave_room(room)
    print(f'Client left auction room: {room}')

# API endpoint for getting current auction data
@app.route('/api/auction/<int:product_id>')
def get_auction_data(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'current_bid': float(product.current_bid or product.start_price),
        'min_increment': float(product.min_increment),
        'time_left': (product.auction_end - datetime.utcnow()).total_seconds() if product.auction_end else None,
        'status': product.status
    })

@app.route('/auctions')
def list_auctions():
    query = Product.query.filter_by(is_auction=True, status='active')
    
    # Filter by search query
    search = request.args.get('q')
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )
    
    # Filter by ending soon
    if request.args.get('ending_soon'):
        soon = datetime.utcnow() + timedelta(hours=24)
        query = query.filter(Product.auction_end <= soon)
    
    # Sort by newest/ending soonest/highest bid
    sort = request.args.get('sort', 'newest')
    if sort == 'ending_soon':
        query = query.order_by(Product.auction_end.asc())
    elif sort == 'highest_bid':
        query = query.order_by(Product.current_bid.desc())
    else:  # newest
        query = query.order_by(Product.id.desc())
    
    auctions = query.all()
    return render_template('auctions.html', auctions=auctions)

# ─── Cart & Wishlist ────────────────────────────────────────────────────────────

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    ci = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if ci:
        ci.quantity += 1
        flash('Increased quantity in cart', 'info')
    else:
        ci = Cart(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(ci)
        flash('Added to cart', 'success')
    db.session.commit()
    return redirect(url_for('cart'))


@app.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    # Check if product exists
    product = Product.query.get_or_404(product_id)
    
    # Check if item is already in wishlist
    existing_item = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if existing_item:
        # Remove from wishlist
        db.session.delete(existing_item)
        flash('Removed from your watchlist', 'info')
    else:
        # Add to wishlist
        wishlist_item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(wishlist_item)
        flash('Added to your watchlist', 'success')
    
    db.session.commit()
    
    # Redirect back to the previous page
    return redirect(request.referrer or url_for('list_auctions'))

@app.route('/add_product', methods=['GET','POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name        = request.form['name']
        desc        = request.form['description']
        price       = float(request.form['price'])
        # now tie it to the logged-in user:
        new_prod = Product(
            name=name,
            description=desc,
            price=price,
            seller_id=current_user.id
        )
        db.session.add(new_prod)
        db.session.commit()
        flash('Your item is now listed!', 'success')
        return redirect(url_for('index'))
    return render_template('add_product.html')



@app.route('/cart')
@login_required
def cart():
    # 1) Fetch all cart rows for this user
    items = Cart.query.filter_by(user_id=current_user.id).all()

    # 2) Build line_items and grand_total
    line_items = []
    grand_total = 0.0

    for ci in items:
        # consistently call it "product"
        product = Product.query.get(ci.product_id)
        subtotal = product.price * ci.quantity
        grand_total += subtotal

        line_items.append({
            'product':    product,
            'quantity':   ci.quantity,
            'subtotal':   subtotal
        })

    # 3) Render the cart.html template with the data
    return render_template(
        'cart.html',
        line_items=line_items,
        grand_total=grand_total
    )


@app.route('/wishlist')
@login_required
def wishlist():
    items    = Wishlist.query.filter_by(user_id=current_user.id).all()
    products = [Product.query.get(i.product_id) for i in items]
    return render_template('wishlist.html', products=products)



def process_payment(order):
    """
    Stubbed payment processor.
    Replace with real API calls as needed.
    """
    return True


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # 1) Load the current user's cart items
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    # 2) Build line_items and grand_total
    line_items = []
    grand_total = 0.0
    for ci in cart_items:
        product = Product.query.get(ci.product_id)
        if not product:
            continue
        subtotal = product.price * ci.quantity
        grand_total += subtotal
        line_items.append({
            'product': product,
            'quantity': ci.quantity,
            'subtotal': subtotal
        })

    if request.method == 'POST':
        # 3) Collect shipping & payment info from form
        shipping_name   = request.form.get('shipping_name', '').strip()
        shipping_addr   = request.form.get('shipping_addr', '').strip()
        payment_method  = request.form.get('payment_method', '').strip()

        # basic validation
        if not shipping_name or not shipping_addr or not payment_method:
            flash('Please fill in all shipping and payment fields.', 'danger')
            return redirect(url_for('checkout'))

        # 4) Create and save the Order
        order = Order(
            user_id=current_user.id,
            shipping_name=shipping_name,
            shipping_addr=shipping_addr,
            payment_method=payment_method,
            total_price=grand_total,
            status='Processing'
        )
        db.session.add(order)
        db.session.commit()

        # 5) Process payment
        if process_payment(order):
            order.status = 'Paid'
            db.session.commit()
            flash('Payment successful! Waiting on seller to provide a tracking number.', 'success')
        else:
            flash('Payment failed. Please try again.', 'danger')
            return redirect(url_for('checkout'))
        

        

        # 6) Move items from Cart into OrderItem, then clear cart
        for ci in cart_items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=ci.product_id,
                quantity=ci.quantity
            ))
            db.session.delete(ci)
        db.session.commit()

        # 7) Finally, send the user to their orders page
        return redirect(url_for('orders'))
    


    

    # GET: Render the checkout form, passing line_items & grand_total
    return render_template(
        'checkout.html',
        line_items=line_items,
        grand_total=grand_total
    )


@app.route('/orders')
@login_required
def orders():
    all_orders = Order.query.filter_by(user_id=current_user.id)\
                            .order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=all_orders)


@app.route('/track', methods=['GET', 'POST'])
def track():
    order = None
    # 1) Check POST first
    if request.method == 'POST':
        tn = request.form.get('tracking_number', '').strip().upper()
    # 2) Or allow ?tracking_number= in the URL
    else:
        tn = request.args.get('tracking_number', '').strip().upper()
    if tn:
        order = Order.query.filter_by(tracking_number=tn).first()
        if not order:
            flash('Invalid tracking number', 'danger')
    return render_template('track.html', order=order)





# ─── Edit a listing ───────────────────────────────────────────────────────────────
@app.route('/edit_product/<int:product_id>', methods=['GET','POST'])
@login_required
def edit_product(product_id):
    prod = Product.query.get_or_404(product_id)
    # only the seller may edit
    if prod.seller_id != current_user.id:
        flash("You don't have permission to edit that.", 'danger')
        return redirect(url_for('my_listings'))

    if request.method == 'POST':
        prod.name        = request.form['name']
        prod.description = request.form['description']
        prod.price       = float(request.form['price'])
        db.session.commit()
        flash('Listing updated.', 'success')
        return redirect(url_for('my_listings'))

    # GET: show existing values in the form
    return render_template('edit_product.html', product=prod)


# ─── Delete a listing ───────────────────────────────────────────────────────────
@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    prod = Product.query.get_or_404(product_id)
    if prod.seller_id != current_user.id:
        flash("You don't have permission to delete that.", 'danger')
        return redirect(url_for('my_listings'))

    db.session.delete(prod)
    db.session.commit()
    flash('Listing removed.', 'info')
    return redirect(url_for('my_listings'))



@app.route('/my_sales')
@login_required
def my_sales():
    # find orders where at least one item is your product
    orders = (
      Order.query
           .join(OrderItem)
           .join(Product)
           .filter(Product.seller_id == current_user.id)
           .order_by(Order.created_at.desc())
           .all()
    )
    return render_template('my_sales.html', orders=orders)

# Support Routes
@app.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')
        priority = request.form.get('priority', 'medium')
        
        if not subject or not message:
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('support'))
            
        ticket = SupportTicket(
            user_id=current_user.id,
            subject=subject,
            message=message,
            priority=priority,
            status='open'
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        flash('Your support ticket has been submitted successfully!', 'success')
        return redirect(url_for('support_tickets'))
    
    return render_template('support.html')

@app.route('/support/tickets')
@login_required
def support_tickets():
    tickets = SupportTicket.query.filter_by(user_id=current_user.id).order_by(SupportTicket.created_at.desc()).all()
    return render_template('support_tickets.html', tickets=tickets)

@app.route('/support/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    # Ensure the user can only view their own tickets
    if ticket.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        flash('You do not have permission to view this ticket', 'danger')
        return redirect(url_for('support_tickets'))
    return render_template('view_ticket.html', ticket=ticket)

@app.route('/support/ticket/<int:ticket_id>/reply', methods=['POST'])
@login_required
def reply_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    # Ensure the user can only reply to their own tickets
    if ticket.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        flash('You do not have permission to reply to this ticket', 'danger')
        return redirect(url_for('support_tickets'))
    
    message = request.form.get('message')
    if not message:
        flash('Message cannot be empty', 'danger')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    # In a real application, you would create a SupportMessage model for replies
    # For now, we'll just update the ticket's message
    ticket.message = f"{ticket.message}\n\n--- New Reply ---\n{message}"
    ticket.status = 'in_progress' if getattr(current_user, 'is_admin', False) else 'waiting_for_response'
    ticket.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Your reply has been submitted', 'success')
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/support/ticket/<int:ticket_id>/close', methods=['POST'])
@login_required
def close_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    # Only the ticket owner or admin can close the ticket
    if ticket.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        flash('You do not have permission to close this ticket', 'danger')
        return redirect(url_for('support_tickets'))
    
    ticket.status = 'closed'
    ticket.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Ticket has been closed', 'success')
    return redirect(url_for('support_tickets'))



# ─── Run ────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # ensure all tables exist
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
