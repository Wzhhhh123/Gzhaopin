from flask import Flask, render_template
from flask import Flask, request, session, redirect, url_for
from flask_babel import Babel, _
app = Flask(__name__)
app.secret_key = 'asdasdasdasd'

# 配置Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['LANGUAGES'] = {
    'en': 'English',
    'zh': '中文'
}

babel = Babel(app)
@babel.localeselector
def get_locale():
    # 如果用户选择了语言并保存在session中，使用该语言
    if 'language' in session:
        return session['language']
    # 否则使用浏览器默认语言
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())
@app.route('/set_language/<language>')
def set_language(language):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))
@app.before_request
def set_language():
    if 'language' not in session:
        session['language'] = 'en'  # 默认英文
# 首页路由
@app.route('/')
def index123():
    if session['language']=="en":
        return render_template('index.html')
    if session['language']=="zh":
        return render_template('index-zh.html')

@app.route('/index.html')
def index():
    if session['language']=="en":
        return render_template('index.html')
    if session['language']=="zh":
        return render_template('index-zh.html')
# 备用首页路由
@app.route('/index-2.html')
def index2():
    return render_template('index-2.html')

@app.route('/index-3.html')
def index3():
    return render_template('index-3.html')

# 关于我们
@app.route('/about-us.html')
def about_us():
    return render_template('about-us.html')

# 工作提醒
@app.route('/alert-jobs.html')
def alert_jobs():
    return render_template('alert-jobs.html')

# 已申请工作
@app.route('/applied-jobs.html')
def applied_jobs():
    return render_template('applied-jobs.html')

# 博客相关
@app.route('/blog.html')
def blog():
    return render_template('blog.html')

@app.route('/blog-details.html')
def blog_details():
    return render_template('blog-details.html')

# 书签
@app.route('/bookmarks.html')
def bookmarks():
    return render_template('bookmarks.html')

# 候选人相关
@app.route('/candidates-listing.html')
def candidates_listing():
    return render_template('candidates-listing.html')

@app.route('/candidates-details.html')
def candidates_details():
    return render_template('candidates-details.html')

# 更改密码
@app.route('/change-password.html')
def change_password():
    return render_template('change-password.html')

# 即将上线
@app.route('/coming-soon.html')
def coming_soon():
    return render_template('coming-soon.html')

# 联系我们
@app.route('/contact-us.html')
def contact_us():
    return render_template('contact-us.html')

# 仪表盘
@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

# 雇主相关
@app.route('/employers-listing.html')
def employers_listing():
    return render_template('employers-listing.html')

@app.route('/employers-details.html')
def employers_details():
    return render_template('employers-details.html')

# 常见问题
@app.route('/faq.html')
def faq():
    return render_template('faq.html')

# 自由职业者
@app.route('/freelancer.html')
def freelancer():
    return render_template('freelancer.html')

# 工作相关
@app.route('/job-listing.html')
def job_listing():
    return render_template('job-listing.html')

@app.route('/job-details.html')
def job_details():
    return render_template('job-details.html')

# 登录注册
@app.route('/log-in-register.html')
def login_register():
    return render_template('log-in-register.html')

# 消息
@app.route('/message.html')
def message():
    return render_template('message.html')

# 发布工作
@app.route('/post-job.html')
def post_job():
    return render_template('post-job.html')

# 价格
@app.route('/pricing.html')
def pricing():
    return render_template('pricing.html')

# 隐私政策
@app.route('/privacy-policy.html')
def privacy_policy():
    return render_template('privacy-policy.html')

# 个人资料
@app.route('/profile.html')
def profile():
    return render_template('profile.html')

# 简历
@app.route('/resume.html')
def resume():
    return render_template('resume.html')

# 条款条件
@app.route('/terms-conditions.html')
def terms_conditions():
    return render_template('terms-conditions.html')

# 推荐
@app.route('/testimonials.html')
def testimonials():
    return render_template('testimonials.html')

# 404页面 - 需要特殊处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5222)