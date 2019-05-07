

from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
# from guess_language import guess_language
from volsteads import mongo
from volsteads.main.forms import EditProfileForm, PostForm
from volsteads.models import User
# from volsteads.translate import translate
from volsteads.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        mongo.db.session.commit()
    g.locale = str(get_locale())

@bp.route('/', methods=['GET', "POST'"])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        # language = guess_language(form.post.data)
        #if language == 'UNKNOWN' or len(language) > 5:
        #    language = ''
        # post = Post(body=form.post.data, author=current_user, language=language)
        # mongo.db.session.add(post)
        # mongo.db.session.commit()
        flash(_('Added to live website.'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    #
    return render_template('eod_form.html', title=_('Home'), form=form)

#
    # posts = local_user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    # next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    # prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    # return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)
