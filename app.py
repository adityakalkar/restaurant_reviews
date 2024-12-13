from flask import Flask, render_template, redirect, url_for, request, session, flash
from forms import RegistrationForm, LoginForm, ReviewForm, EditReviewForm
from flask_bcrypt import Bcrypt
from models import create_user, find_user_by_email, find_user_by_id

from models import (
    create_user,
    find_user_by_email,
    create_review,
    get_all_reviews,
    get_reviews_by_user,
    update_review,
    search_restaurants,
    find_review_by_id,
    delete_review
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    """Render the homepage."""
    return render_template('base.html', businesses=None)  



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        create_user(form.username.data, form.email.data, hashed_password)
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = find_user_by_email(form.email.data)
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            flash(f'Welcome, {user["username"]}!', 'success')
            return redirect(url_for('home'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/add_review', methods=['GET', 'POST'])
def add_review():
    if 'user_id' not in session:
        flash('Please log in to write a review.', 'danger')
        return redirect(url_for('login'))

    form = ReviewForm()
    if form.validate_on_submit():
        create_review(
            restaurant_name=form.restaurant_name.data,
            rating=form.rating.data,
            comment=form.comment.data,
            user_id=session['user_id'],
            username=session['username'],
        )
        flash('Review added successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_review.html', form=form)

@app.route('/my_reviews')
def my_reviews():
    """Display all reviews submitted by the logged-in user."""
    if 'user_id' not in session:
        flash('Please log in to view your reviews.', 'danger')
        return redirect(url_for('login'))

    user_reviews = list(get_reviews_by_user(session['user_id']))  
    return render_template('my_reviews.html', reviews=user_reviews)




@app.route('/edit_review/<review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    """Allow logged-in users to edit their reviews."""
    if 'user_id' not in session:
        flash('Please log in to edit your review.', 'danger')
        return redirect(url_for('login'))

    review = find_review_by_id(review_id)
    if not review or review['user_id'] != session['user_id']:
        flash('You can only edit your own reviews.', 'danger')
        return redirect(url_for('home'))

    form = EditReviewForm()
    if form.validate_on_submit():
        update_review(review_id, form.rating.data, form.comment.data)
        flash('Your review has been updated!', 'success')
        return redirect(url_for('my_reviews'))


    form.rating.data = review['rating']
    form.comment.data = review['comment']
    return render_template('edit_review.html', form=form, review=review)

@app.route('/delete_review/<review_id>', methods=['POST'])
def delete_review_route(review_id):
    """Allow logged-in users to delete their reviews."""
    if 'user_id' not in session:
        flash('Please log in to delete your review.', 'danger')
        return redirect(url_for('login'))

    review = find_review_by_id(review_id)
    if not review or review['user_id'] != session['user_id']:
        flash('You can only delete your own reviews.', 'danger')
        return redirect(url_for('home'))

    delete_review(review_id)
    flash('Your review has been deleted!', 'success')
    return redirect(url_for('my_reviews'))

@app.route('/search', methods=['POST'])
def search():
    """Search for restaurants using Yelp API."""
    term = request.form.get('term')
    location = request.form.get('location')
    businesses = None
    if term and location:
        try:
            businesses = search_restaurants(term, location)
        except Exception as e:
            print(f"Error fetching search results: {e}")
    return render_template('base.html', businesses=businesses)



if __name__ == '__main__':
    app.run(debug=True)
