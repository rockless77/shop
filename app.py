import os
from flask import (
    Flask, render_template, request, redirect, 
    url_for, session, flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import (
    LoginManager, UserMixin, login_user, 
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
# ─── App & Extensions ────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db      = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ─── Models ───────────────────────────────────────────────────────────────────────

class User(db.Model, UserMixin):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(150), unique=True, nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    cart_items     = db.relationship('Cart',     backref='user', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='user', lazy=True)
    orders         = db.relationship('Order',    backref='user', lazy=True)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Product(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price       = db.Column(db.Float, nullable=False)

    order_items = db.relationship('OrderItem', backref='product', lazy=True)

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
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)           # ← new


# ─── Flask-Login Loader ─────────────────────────────────────────────────────────

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Public Routes ───────────────────────────────────────────────────────────────

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))
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


@app.route('/order/<int:oid>/update', methods=['POST'])
@login_required
def update_order(oid):
    # ideally check current_user.is_admin
    new_status = request.form['status']
    o = Order.query.get_or_404(oid)
    o.status = new_status
    db.session.commit()
    flash(f'Order {oid} set to {new_status}', 'info')
    return redirect(url_for('orders'))


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


@app.route('/add-to-wishlist/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    if not Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first():
        db.session.add(Wishlist(user_id=current_user.id, product_id=product_id))
        db.session.commit()
        flash('Added to wishlist!', 'success')
    else:
        flash('Already in wishlist.', 'info')
    return redirect(url_for('index'))

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        product_name = request.form['name']
        product_description = request.form['description']
        product_price = request.form['price']
        
        new_product = Product(name=product_name, description=product_description, price=product_price)
        db.session.add(new_product)
        db.session.commit()

        flash("Product added successfully!")
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
            # generate a tracking number
            order.tracking_number = uuid.uuid4().hex[:12].upper()
            db.session.commit()
            flash(f'Payment successful! Your tracking #: {order.tracking_number}', 'success')
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



# ─── Run ────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # ensure all tables exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
