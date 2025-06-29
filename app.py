from flask import Flask, render_template

app = Flask(__name__)

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 备用首页路由
@app.route('/index-2')
def index2():
    return render_template('index-2.html')

@app.route('/index-3')
def index3():
    return render_template('index-3.html')

# 关于我们
@app.route('/about-us')
def about_us():
    return render_template('about-us.html')

# 工作提醒
@app.route('/alert-jobs')
def alert_jobs():
    return render_template('alert-jobs.html')

# 已申请工作
@app.route('/applied-jobs')
def applied_jobs():
    return render_template('applied-jobs.html')

# 博客相关
@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/blog-details')
def blog_details():
    return render_template('blog-details.html')

# 书签
@app.route('/bookmarks')
def bookmarks():
    return render_template('bookmarks.html')

# 候选人相关
@app.route('/candidates-listing')
def candidates_listing():
    return render_template('candidates-listing.html')

@app.route('/candidates-details')
def candidates_details():
    return render_template('candidates-details.html')

# 更改密码
@app.route('/change-password')
def change_password():
    return render_template('change-password.html')

# 即将上线
@app.route('/coming-soon')
def coming_soon():
    return render_template('coming-soon.html')

# 联系我们
@app.route('/contact-us')
def contact_us():
    return render_template('contact-us.html')

# 仪表盘
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 雇主相关
@app.route('/employers-listing')
def employers_listing():
    return render_template('employers-listing.html')

@app.route('/employers-details')
def employers_details():
    return render_template('employers-details.html')

# 常见问题
@app.route('/faq')
def faq():
    return render_template('faq.html')

# 自由职业者
@app.route('/freelancer')
def freelancer():
    return render_template('freelancer.html')

# 工作相关
@app.route('/job-listing')
def job_listing():
    return render_template('job-listing.html')

@app.route('/job-details')
def job_details():
    return render_template('job-details.html')

# 登录注册
@app.route('/log-in-register')
def login_register():
    return render_template('log-in-register.html')

# 消息
@app.route('/message')
def message():
    return render_template('message.html')

# 发布工作
@app.route('/post-job')
def post_job():
    return render_template('post-job.html')

# 价格
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# 隐私政策
@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

# 个人资料
@app.route('/profile')
def profile():
    return render_template('profile.html')

# 简历
@app.route('/resume')
def resume():
    return render_template('resume.html')

# 条款条件
@app.route('/terms-conditions')
def terms_conditions():
    return render_template('terms-conditions.html')

# 推荐
@app.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')

# 404页面 - 需要特殊处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)