from flask import Flask, render_template
from flask import Flask, request, session, redirect, url_for
from flask_babel import Babel, _
from werkzeug.security import generate_password_hash, check_password_hash
from db import init_db_config, connect_db
from functools import wraps
from flask import Flask, request, redirect, url_for, session, flash, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import os
import uuid
from werkzeug.utils import secure_filename
import mimetypes

from functools import wraps
app = Flask(__name__)
app.config["SECRET_KEY"] = '79537d00f4834892986f09a100aa1edf'
# 配置文件上传
# 配置文件上传
UPLOAD_FOLDER = 'static/uploads/resumes'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
init_db_config()
# 配置Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['LANGUAGES'] = {
    'en': 'English',
    'zh': '中文'
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Wzh010310@192.168.1.185/job_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



def allowed_file(filename):
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def get_safe_filename(filename):
    """生成安全的文件名，保持原始扩展名"""
    # 首先从原始文件名提取扩展名
    original_ext = None
    if '.' in filename:
        original_ext = filename.rsplit('.', 1)[1].lower()

    # 验证扩展名是否允许
    if original_ext and original_ext in ALLOWED_EXTENSIONS:
        ext = original_ext
    else:
        # 如果扩展名不允许或不存在，使用默认的pdf
        ext = 'pdf'

    # 生成安全的文件名（使用UUID）
    safe_filename = f"{uuid.uuid4().hex}.{ext}"

    print(f"原始文件名: {filename}")
    print(f"提取的扩展名: {original_ext}")
    print(f"最终使用的扩展名: {ext}")
    print(f"生成的文件名: {safe_filename}")

    return safe_filename

def create_upload_folder():
    """创建上传文件夹"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    education = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(100))
    job_type = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(50))
    deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_featured = db.Column(db.Boolean, default=False)
    is_urgent = db.Column(db.Boolean, default=False)
    logo = db.Column(db.String(100), default='hot-jobs-1.png')
# 简历申请模型
# 简历申请模型
class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    education = db.Column(db.String(50))
    work_experience = db.Column(db.Text)
    additional_info = db.Column(db.Text)
    resume_filename = db.Column(db.String(255))  # 服务器上的文件名
    original_filename = db.Column(db.String(255))  # 原始文件名
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, rejected, accepted

    # 关系
    job = db.relationship('Job', backref=db.backref('applications', lazy=True))
# 生成示例数据
def create_sample_data():
    # 检查是否已有数据
    if Job.query.count() > 0:
        print("数据库中已有数据，跳过示例数据生成")
        return

    print("开始生成示例数据...")

    # 公司列表
    companies = [
        "北京富鹏商务服务有限公司", "富鹏翻译服务中心", "富鹏技术咨询有限公司",
        "富鹏国际交流中心", "富鹏会展服务有限公司", "富鹏文化艺术交流中心"
    ]

    # 职位列表基于业务范围
    job_titles = [
        "翻译服务专员", "技术开发工程师", "技术咨询顾问", "国际交流协调员",
        "会展活动策划", "文化艺术交流专员", "商务咨询顾问", "市场营销策划",
        "俄罗斯信息咨询顾问", "中亚国家信息咨询顾问", "公共安全管理咨询师",
        "教育咨询顾问", "技术推广专员", "技术转让顾问", "高级翻译项目经理",
        "多语言翻译专员", "软件工程师", "前端开发工程师", "后端开发工程师",
        "数据分析师", "系统架构师", "技术解决方案顾问"
    ]

    # 详细的职位描述
    descriptions = {
        "翻译服务专员": "负责中俄/中亚语言翻译工作，提供专业的笔译和口译服务，协助客户进行商务沟通和技术文档翻译。要求熟练掌握至少一门外语，具备优秀的语言表达能力和跨文化沟通能力。",
        "技术开发工程师": "负责公司技术开发项目，包括网站开发、系统集成和技术解决方案的实施。熟练掌握Python、Java等编程语言，有丰富的项目开发经验。",
        "技术咨询顾问": "为客户提供专业的技术咨询服务，包括技术方案设计、技术问题解决和技术培训。具备扎实的技术背景和良好的客户沟通能力。",
        "国际交流协调员": "组织和管理国际交流活动，协调中外双方的合作事宜，促进文化交流和商务合作。具备优秀的组织协调能力和外语水平。",
        "会展活动策划": "策划和执行各类会议及展览活动，包括活动方案设计、现场管理和客户服务。具备创意策划能力和项目管理经验。",
        "文化艺术交流专员": "组织文化艺术交流活动，促进中外文化艺术的交流与合作。对文化艺术有深入了解，具备优秀的活动组织能力。",
        "商务咨询顾问": "为客户提供商务咨询服务，包括市场分析、商业策划和投资咨询。具备丰富的商务知识和分析能力。",
        "市场营销策划": "制定和执行市场营销策略，进行市场调研和品牌推广活动。具备创意策划能力和市场敏感度。",
        "俄罗斯信息咨询顾问": "提供俄罗斯市场信息咨询服务，包括政策法规、市场环境和商业机会分析。精通俄语，了解俄罗斯市场环境。",
        "中亚国家信息咨询顾问": "提供中亚国家市场信息咨询服务，协助客户开拓中亚市场。熟悉中亚国家政治经济环境，具备区域研究背景。",
        "公共安全管理咨询师": "提供公共安全管理咨询服务，包括安全评估和应急预案制定。具备安全管理相关知识和实践经验。",
        "教育咨询顾问": "提供教育咨询服务，包括留学咨询、教育培训和学术交流。熟悉教育体系和留学政策。",
        "技术推广专员": "负责技术推广工作，包括技术展示、推广活动和客户培训。具备良好的演讲能力和技术理解能力。",
        "技术转让顾问": "协助客户进行技术转让交易，包括技术评估、合同谈判和项目实施。具备技术背景和法律知识。",
        "高级翻译项目经理": "管理翻译项目团队，协调项目进度，确保翻译质量和交付时间。具备项目管理经验和团队领导能力。",
        "多语言翻译专员": "负责多种语言的翻译工作，包括文档翻译、现场口译和本地化服务。精通至少两种外语。"
    }

    # 生成80个示例职位
    jobs_to_create = []
    for i in range(80):
        title = random.choice(job_titles)
        company = random.choice(companies)

        job = Job(
            title=title,
            company=company,
            description=descriptions.get(title, "优秀的职业发展机会，具有竞争力的薪酬待遇和良好的工作环境，欢迎加入我们的团队！"),
            requirements="具有良好的沟通能力和团队合作精神，具备相关领域的工作经验，能够适应快节奏的工作环境。",
            education=random.choice(["大专", "本科", "硕士", "博士"]),
            experience=random.choice(["应届毕业生", "1-2年", "3-5年", "5年以上"]),
            location=random.choice(["北京", "上海", "广州", "深圳", "杭州", "成都", "远程工作"]),
            salary=random.choice(["面议", "8-15K", "15-25K", "25-40K", "40K以上"]),
            job_type=random.choice(["全职", "兼职", "实习", "合同制"]),
            level=random.choice(["初级", "中级", "高级", "经理", "总监"]),
            deadline=datetime.utcnow() + timedelta(days=random.randint(1, 90)),
            is_featured=random.choice([True, False, False]),
            is_urgent=random.choice([True, False, False, False]),
            logo=f"hot-jobs-{random.randint(1, 10)}.png"
        )

        jobs_to_create.append(job)

    # 批量插入
    db.session.bulk_save_objects(jobs_to_create)
    db.session.commit()

    print(f"成功生成 {len(jobs_to_create)} 个示例职位")
def init_database():
    with app.app_context():
        db.create_all()
        create_upload_folder()  # 创建上传目录
        if Job.query.count() == 0:
            create_sample_data()
# 登录装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('请先登录。', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
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
#     if session['language']=="en":
#         return render_template('job-listing.html')
#     if session['language']=="zh":
#         return render_template('job-listing-zh.html')
# 获取查询参数
# 获取查询参数
    # 获取查询参数
    # 获取所有查询参数
    search = request.args.get('search', '')
    job_type = request.args.get('job_type', '')
    location = request.args.get('location', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # 构建基础查询
    base_query = Job.query

    # 应用筛选条件
    if search:
        base_query = base_query.filter(
            db.or_(
                Job.title.contains(search),
                Job.description.contains(search),
                Job.company.contains(search),
                Job.requirements.contains(search)
            )
        )
    if job_type:
        base_query = base_query.filter(Job.job_type == job_type)
    if location:
        base_query = base_query.filter(
            db.or_(
                Job.location.contains(location),
                Job.location.like(f'%{location}%')
            )
        )

    # 分页
    pagination = base_query.order_by(Job.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # 获取统计信息（用于侧边栏计数）
    stats_query = Job.query
    if search:
        stats_query = stats_query.filter(
            db.or_(
                Job.title.contains(search),
                Job.description.contains(search),
                Job.company.contains(search),
                Job.requirements.contains(search)
            )
        )
    if location:
        stats_query = stats_query.filter(Job.location.contains(location))

    # 计算各种类型的职位数量
    job_types_count = {
        '全职': stats_query.filter(Job.job_type == '全职').count(),
        '兼职': stats_query.filter(Job.job_type == '兼职').count(),
        '实习': stats_query.filter(Job.job_type == '实习').count(),
        '合同制': stats_query.filter(Job.job_type == '合同制').count()
    }

    total_jobs = stats_query.count()

    return render_template('job-listing-zh.html',
                         jobs=pagination.items,
                         pagination=pagination,
                         total_jobs=total_jobs,
                         job_types_count=job_types_count,
                         current_search=search,
                         current_job_type=job_type,
                         current_location=location)


@app.route('/job/<int:job_id>', methods=['GET', 'POST'])
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)

    # 获取相似职位
    similar_jobs = Job.query.filter(
        Job.job_type == job.job_type,
        Job.id != job.id
    ).limit(3).all()

    if request.method == 'POST':
        try:
            # 验证表单数据
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            education = request.form.get('education', '').strip()
            work_experience = request.form.get('work_experience', '').strip()
            additional_info = request.form.get('additional_info', '').strip()
            agree_terms = request.form.get('agree_terms')

            # 基本验证
            if not all([name, phone, email, agree_terms]):
                return render_template('job-details.html',
                                     job=job,
                                     similar_jobs=similar_jobs,
                                     error_message='请填写所有必填字段并同意隐私政策。')

            # 处理文件上传
            if 'resume' not in request.files:
                return render_template('job-details.html',
                                     job=job,
                                     similar_jobs=similar_jobs,
                                     error_message='请上传简历文件。')

            resume_file = request.files['resume']

            if resume_file.filename == '':
                return render_template('job-details.html',
                                     job=job,
                                     similar_jobs=similar_jobs,
                                     error_message='请选择要上传的简历文件。')

            # 检查文件类型
            if not allowed_file(resume_file.filename):
                return render_template('job-details.html',
                                     job=job,
                                     similar_jobs=similar_jobs,
                                     error_message='不支持的文件格式。请上传PDF、DOC、DOCX、JPG或PNG格式的文件。')

            # 检查文件大小
            resume_file.seek(0, os.SEEK_END)
            file_size = resume_file.tell()
            resume_file.seek(0)

            if file_size == 0:
                return render_template('job-details.html',
                                     job=job,
                                     similar_jobs=similar_jobs,
                                     error_message='文件为空，请重新选择文件。')

            if file_size > MAX_FILE_SIZE:
                return render_template('job-details.html',
                                     job=job,
                                     similar_jobs=similar_jobs,
                                     error_message='文件大小不能超过5MB。')

            # 生成安全的文件名（保持原始扩展名）
            unique_filename = get_safe_filename(resume_file.filename)

            # 确保上传目录存在
            create_upload_folder()

            # 保存文件
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            resume_file.save(resume_path)

            # 验证文件是否成功保存
            if not os.path.exists(resume_path):
                return render_template('job-details.html',
                                     job=job,
                                     similar_jobs=similar_jobs,
                                     error_message='文件保存失败，请重试。')

            # 保存申请信息到数据库
            application = JobApplication(
                job_id=job.id,
                name=name,
                phone=phone,
                email=email,
                education=education,
                work_experience=work_experience,
                additional_info=additional_info,
                resume_filename=unique_filename,
                original_filename=resume_file.filename  # 保存原始文件名
            )

            db.session.add(application)
            db.session.commit()

            return render_template('job-details.html',
                                 job=job,
                                 similar_jobs=similar_jobs,
                                 success_message='申请提交成功！我们会尽快审核并与您联系。')

        except Exception as e:
            db.session.rollback()
            # 如果数据库保存失败，删除已上传的文件
            if 'resume_path' in locals() and os.path.exists(resume_path):
                os.remove(resume_path)

            print(f"Error in job_detail: {str(e)}")  # 用于调试
            return render_template('job-details.html',
                                 job=job,
                                 similar_jobs=similar_jobs,
                                 error_message='系统错误，请稍后重试。')

    return render_template('job-details.html', job=job, similar_jobs=similar_jobs)
@app.route('/api/jobs')
def api_jobs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    jobs = Job.query.paginate(page=page, per_page=per_page, error_out=False)

    jobs_data = []
    for job in jobs.items:
        jobs_data.append({
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'salary': job.salary,
            'job_type': job.job_type,
            'education': job.education,
            'experience': job.experience,
            'deadline': job.deadline.strftime('%Y年%m月%d日'),
            'is_featured': job.is_featured,
            'is_urgent': job.is_urgent
        })

    return jsonify({
        'jobs': jobs_data,
        'total': jobs.total,
        'pages': jobs.pages,
        'current_page': page
    })

@app.route('/api/job-stats')
def job_stats():
    """获取职位统计信息"""
    total_jobs = Job.query.count()
    featured_jobs = Job.query.filter_by(is_featured=True).count()
    urgent_jobs = Job.query.filter_by(is_urgent=True).count()

    # 按类型统计
    type_stats = db.session.query(
        Job.job_type,
        db.func.count(Job.id)
    ).group_by(Job.job_type).all()

    # 按地点统计
    location_stats = db.session.query(
        Job.location,
        db.func.count(Job.id)
    ).group_by(Job.location).all()

    return jsonify({
        'total_jobs': total_jobs,
        'featured_jobs': featured_jobs,
        'urgent_jobs': urgent_jobs,
        'type_stats': dict(type_stats),
        'location_stats': dict(location_stats)
    })



# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_username = request.form.get('email-username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        conn = connect_db()
        cursor = conn.cursor()

        try:
            # 查询用户是否存在
            cursor.execute("""
                SELECT * FROM users
                WHERE username = %s OR email = %s
            """, (email_username, email_username))
            user = cursor.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                session['role'] = user['role']
                session['first_name'] = user.get('first_name', '')
                session['last_name'] = user.get('last_name', '')

                if remember:
                    session.permanent = True

                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username/email or password', 'danger')
        except Exception as e:
            flash('An error occurred during login', 'danger')
            app.logger.error(f"Login error: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    if session['language']=="en":
        return render_template('log-in-register.html', show_form='login')
    if session['language']=="zh":
        return render_template('log-in-register-zh.html', show_form='login')





# 注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 获取表单数据
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        address = request.form.get('address')
        user_type = request.form.get('user_type')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        terms = request.form.get('terms')

        # 验证数据
        if not terms:
            flash('You must agree to the terms and conditions', 'danger')
            if session['language']=="en":
                return render_template('log-in-register.html', show_form='register')
            if session['language']=="zh":
                return render_template('log-in-register-zh.html', show_form='register')




        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            if session['language']=="en":
                return render_template('log-in-register.html', show_form='register')
            if session['language']=="zh":
                return render_template('log-in-register-zh.html', show_form='register')



        conn = connect_db()
        cursor = conn.cursor()

        try:
            # 检查用户名或邮箱是否已存在
            cursor.execute("""
                SELECT id FROM users
                WHERE username = %s OR email = %s
            """, (username, email))

            if cursor.fetchone():
                flash('Username or email already exists', 'danger')
                if session['language']=="en":
                    return render_template('log-in-register.html', show_form='register')
                if session['language']=="zh":
                    return render_template('log-in-register-zh.html', show_form='register')



            # 创建用户
            password_hash = generate_password_hash(password)

            cursor.execute("""
                INSERT INTO users (
                    first_name, last_name, username, email, phone,
                    dob, address, role, password_hash, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                first_name, last_name, username, email, phone,
                dob, address, user_type, password_hash
            ))

            conn.commit()

            if session['language']=="en":
                flash('Registration successful! Please log in.', 'success')
                return render_template('log-in-register.html', show_form='login')
            if session['language']=="zh":
                flash('注册成功，请登录！', 'success')
                return render_template('log-in-register-zh.html', show_form='login')


        except Exception as e:
            conn.rollback()
            flash('An error occurred during registration', 'danger')
            app.logger.error(f"Registration error: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    if session['language']=="en":
        return render_template('log-in-register.html', show_form='register')
    if session['language']=="zh":
        return render_template('log-in-register-zh.html', show_form='register')


# 退出登录
@app.route('/logout')
def logout():
    ss=session['language']
    session.clear()
    session['language']=ss
    print("session after clear:", dict(session))
    flash('已退出登录。', 'info')
    return redirect(url_for('login'))
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
    try:
        with app.app_context():
            db.create_all()
            create_sample_data()
            app.run(debug=True,host='0.0.0.0',port=5222)
    except Exception as e:
            print(f"启动错误: {e}")
            print("请确保：")
            print("1. MySQL服务已启动")
            print("2. 数据库 'job_db' 已创建")
            print("3. 用户名和密码正确")
            print("4. 已安装 pymysql: pip install pymysql")