from flask import Flask, render_template, send_file
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
import re
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



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否登录
        if 'username' not in session:
            flash('请先登录。', 'warning')
            return redirect(url_for('login'))

        # 检查用户角色是否为admin
        if session.get('role') != 'admin':
            flash('您没有权限访问管理员页面', 'danger')
            return redirect(url_for('dashboard'))

        return f(*args, **kwargs)
    return decorated_function
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

    # 职位列表基于业务范围 - 确保覆盖所有分类
    job_titles = [
        # 翻译服务类
        "翻译服务专员", "高级翻译项目经理", "多语言翻译专员", "俄语翻译", "英语翻译",

        # 技术开发类
        "技术开发工程师", "软件工程师", "前端开发工程师", "后端开发工程师",
        "数据分析师", "系统架构师", "Java开发工程师", "Python开发工程师",

        # 技术咨询类
        "技术咨询顾问", "技术解决方案顾问", "IT咨询顾问", "业务咨询顾问",

        # 技术交流类
        "国际交流协调员", "技术交流专员", "国际合作专员",

        # 技术转让类
        "技术转让顾问", "知识产权顾问",

        # 技术推广类
        "技术推广专员", "产品推广专员",

        # 会议及展览服务类
        "会展活动策划", "会议服务专员", "展览策划", "活动执行",

        # 文化艺术交流类
        "文化艺术交流专员", "文化活动策划", "艺术项目协调员",

        # 社会经济咨询类
        "商务咨询顾问", "经济分析师", "投资顾问", "商业策划师",

        # 公共安全管理咨询类
        "公共安全管理咨询师", "安全顾问", "风险管理师",

        # 教育咨询类
        "教育咨询顾问", "留学顾问", "培训顾问",

        # 市场营销类
        "市场营销策划", "市场推广专员", "品牌策划", "数字营销专员",

        # 俄罗斯信息咨询类
        "俄罗斯信息咨询顾问", "俄语商务顾问", "俄罗斯市场分析师",

        # 中亚信息咨询类
        "中亚国家信息咨询顾问", "中亚市场分析师", "中亚商务专员"
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
        "多语言翻译专员": "负责多种语言的翻译工作，包括文档翻译、现场口译和本地化服务。精通至少两种外语。",
        # 新增职位的描述
        "软件工程师": "负责软件系统的设计、开发和维护工作，参与产品需求分析和技术方案制定。",
        "数据分析师": "负责业务数据的收集、分析和可视化，为决策提供数据支持。",
        "系统架构师": "设计系统架构方案，确保系统的可扩展性、安全性和高性能。",
        "俄语翻译": "负责中俄双语翻译工作，包括商务文件翻译和现场口译服务。",
        "英语翻译": "负责中英双语翻译工作，确保翻译质量和专业性。",
        "IT咨询顾问": "为客户提供IT战略规划、系统选型和数字化转型咨询服务。",
        "国际合作专员": "负责国际项目的协调和管理，促进跨国合作与交流。",
        "知识产权顾问": "提供知识产权相关的咨询服务，包括专利、商标和技术转让。",
        "产品推广专员": "负责公司产品和服务的市场推广工作，制定推广策略并执行。",
        "展览策划": "策划和组织各类展览活动，包括展位设计、展商协调和现场管理。",
        "活动执行": "负责活动的现场执行工作，确保活动顺利进行。",
        "艺术项目协调员": "协调艺术项目的实施，管理项目进度和资源分配。",
        "经济分析师": "进行市场研究和经济分析，为客户提供投资建议。",
        "风险管理师": "识别和评估业务风险，制定风险管理策略和应急预案。",
        "留学顾问": "提供留学咨询和申请服务，协助学生完成留学规划。",
        "培训顾问": "设计和实施培训项目，提升员工专业技能和综合素质。",
        "品牌策划": "负责品牌战略规划和品牌形象建设，提升品牌价值。",
        "数字营销专员": "执行数字营销策略，包括社交媒体营销、搜索引擎优化等。",
        "俄语商务顾问": "为对俄业务提供商务咨询和语言支持服务。",
        "俄罗斯市场分析师": "分析俄罗斯市场动态和商业机会，提供市场进入策略。",
        "中亚市场分析师": "研究中亚国家市场环境，为企业拓展中亚市场提供决策支持。",
        "中亚商务专员": "负责中亚地区的商务拓展和客户关系维护。"
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
    """首页 - 显示分类统计和紧急招聘"""
    # 获取职位分类统计
    categories = {
        '翻译服务': Job.query.filter(
            Job.title.contains('翻译') |
            Job.title.contains('语言')
        ).count(),
        '技术开发': Job.query.filter(
            Job.title.contains('开发') |
            Job.title.contains('工程') |
            Job.title.contains('软件') |
            Job.title.contains('架构') |
            Job.title.contains('数据')
        ).count(),
        '技术咨询': Job.query.filter(
            Job.title.contains('咨询') |
            Job.title.contains('顾问')
        ).count(),
        '技术交流': Job.query.filter(
            Job.title.contains('交流') |
            Job.title.contains('国际') |
            Job.title.contains('协调')
        ).count(),
        '技术转让': Job.query.filter(Job.title.contains('转让')).count(),
        '技术推广': Job.query.filter(Job.title.contains('推广')).count(),
        '会议及展览服务': Job.query.filter(
            Job.title.contains('会议') |
            Job.title.contains('会展') |
            Job.title.contains('展览')
        ).count(),
        '组织文化艺术交流活动': Job.query.filter(
            Job.title.contains('文化') |
            Job.title.contains('艺术')
        ).count(),
        '社会经济咨询服务': Job.query.filter(
            Job.title.contains('商务') |
            Job.title.contains('经济')
        ).count(),
        '公共安全管理咨询服务': Job.query.filter(
            Job.title.contains('安全') |
            Job.title.contains('管理')
        ).count(),
        '教育咨询服务': Job.query.filter(Job.title.contains('教育')).count(),
        '市场营销策划': Job.query.filter(
            Job.title.contains('市场') |
            Job.title.contains('营销')
        ).count(),
        '俄罗斯信息咨询服务': Job.query.filter(Job.title.contains('俄罗斯')).count(),
        '中亚国家信息咨询服务': Job.query.filter(Job.title.contains('中亚')).count()
    }

    # 获取紧急招聘职位
    urgent_jobs = Job.query.filter_by(is_urgent=True).order_by(Job.created_at.desc()).limit(4).all()

    # 获取推荐职位（精选职位）
    featured_jobs = Job.query.filter_by(is_featured=True).order_by(Job.created_at.desc()).limit(6).all()

    # 获取最新职位
    latest_jobs = Job.query.order_by(Job.created_at.desc()).limit(6).all()

    # 获取统计数据
    stats = {
        'total_jobs': Job.query.count(),
        'urgent_jobs': Job.query.filter_by(is_urgent=True).count(),
        'full_time_jobs': Job.query.filter_by(job_type='全职').count(),
        'remote_jobs': Job.query.filter_by(location='远程工作').count(),
        'featured_jobs_count': Job.query.filter_by(is_featured=True).count(),
        'new_today': Job.query.filter(Job.created_at >= datetime.utcnow().date()).count()
    }
    if session['language']=="en":
        return render_template('index.html',
                             categories=categories,
                             urgent_jobs=urgent_jobs,
                             featured_jobs=featured_jobs,
                             latest_jobs=latest_jobs,
                             stats=stats)
    if session['language']=="zh":
        return render_template('index-zh.html',
                             categories=categories,
                             urgent_jobs=urgent_jobs,
                             featured_jobs=featured_jobs,
                             latest_jobs=latest_jobs,
                             stats=stats)



@app.route('/index.html')
def index():
    return redirect(url_for('index123'))
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
    similar_jobs = Job.query.filter(
        Job.job_type == job.job_type,
        Job.id != job.id
    ).limit(3).all()

    def render_job_detail(msg=None, success=False):
        """统一渲染模板，减少重复"""
        return render_template(
            'job-details.html',
            job=job,
            similar_jobs=similar_jobs,
            **({'success_message': msg} if success else {'error_message': msg}) if msg else {}
        )

    if request.method == 'POST':
        try:
            # 获取表单数据
            form = {k: request.form.get(k, '').strip() for k in
                    ['name', 'phone', 'email', 'education', 'work_experience', 'additional_info']}
            agree_terms = request.form.get('agree_terms')
            resume_file = request.files.get('resume')

            # 基本验证
            if not all([form['name'], form['phone'], form['email'], agree_terms]):
                return render_job_detail('请填写所有必填字段并同意隐私政策。')

            if not resume_file or resume_file.filename == '':
                return render_job_detail('请上传简历文件。')

            if not allowed_file(resume_file.filename):
                return render_job_detail('不支持的文件格式，请上传 PDF、DOC、DOCX、JPG 或 PNG。')

            # 检查文件大小
            resume_file.seek(0, os.SEEK_END)
            size = resume_file.tell()
            resume_file.seek(0)
            if size == 0:
                return render_job_detail('文件为空，请重新选择文件。')
            if size > MAX_FILE_SIZE:
                return render_job_detail('文件大小不能超过5MB。')

            # 保存文件
            unique_filename = get_safe_filename(resume_file.filename)
            create_upload_folder()
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            resume_file.save(resume_path)

            if not os.path.exists(resume_path):
                return render_job_detail('文件保存失败，请重试。')

            # 保存数据库
            db.session.add(JobApplication(
                job_id=job.id,
                resume_filename=unique_filename,
                original_filename=resume_file.filename,
                **form
            ))
            db.session.commit()

            return render_job_detail('申请提交成功！我们会尽快审核并与您联系。', success=True)

        except Exception as e:
            db.session.rollback()
            if 'resume_path' in locals() and os.path.exists(resume_path):
                os.remove(resume_path)
            print(f"Error in job_detail: {e}")
            return render_job_detail('系统错误，请稍后重试。')

    return render_job_detail()

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
                return redirect(url_for('index123'))
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
    return render_template('post-resume-zh.html')

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
# 提交简历页面 - 可选择职位
@app.route('/post-resume.html', methods=['GET', 'POST'])
def post_resume():
    # 获取筛选参数
    search = request.args.get('search', '')
    job_type = request.args.get('job_type', '')
    location = request.args.get('location', '')
    selected_job_id = request.args.get('selected_job', type=int)

    # 基础职位查询（未过期）
    base_query = Job.query.filter(Job.deadline >= datetime.utcnow())

    if search:
        base_query = base_query.filter(db.or_(
            Job.title.contains(search),
            Job.description.contains(search),
            Job.company.contains(search),
            Job.requirements.contains(search)
        ))
    if job_type:
        base_query = base_query.filter(Job.job_type == job_type)
    if location:
        base_query = base_query.filter(Job.location.contains(location))

    jobs = base_query.order_by(Job.created_at.desc()).all()
    selected_job = Job.query.get(selected_job_id) if selected_job_id else None

    def render_page(msg=None, success=False):
        """统一渲染模板，减少重复"""
        return render_template(
            'post-resume-zh.html',
            jobs=jobs,
            search=search,
            job_type=job_type,
            location=location,
            selected_job_id=selected_job_id,
            selected_job=selected_job,
            **({'success_message': msg} if success else {'error_message': msg}) if msg else {}
        )

    if request.method == 'POST':
        try:
            # 表单字段
            form = {k: request.form.get(k, '').strip() for k in
                    ['name', 'phone', 'email', 'education', 'work_experience', 'additional_info']}
            agree_terms = request.form.get('agree_terms')
            selected_job_id = request.form.get('job_id', type=int)
            resume_file = request.files.get('resume')

            # 验证基本字段
            if not all([form['name'], form['phone'], form['email'], agree_terms]):
                return render_page('请填写所有必填字段并同意隐私政策。')

            if not selected_job_id:
                return render_page('请选择要申请的职位。')

            selected_job = Job.query.filter(
                Job.id == selected_job_id,
                Job.deadline >= datetime.utcnow()
            ).first()
            if not selected_job:
                return render_page('选择的职位不存在或已过期。')

            # 验证上传文件
            if not resume_file or resume_file.filename == '':
                return render_page('请上传简历文件。')

            if not allowed_file(resume_file.filename):
                return render_page('不支持的文件格式，请上传 PDF、DOC、DOCX、JPG 或 PNG。')

            resume_file.seek(0, os.SEEK_END)
            size = resume_file.tell()
            resume_file.seek(0)
            if size == 0:
                return render_page('文件为空，请重新选择文件。')
            if size > MAX_FILE_SIZE:
                return render_page('文件大小不能超过5MB。')

            # 保存文件
            unique_filename = get_safe_filename(resume_file.filename)
            create_upload_folder()
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            resume_file.save(resume_path)
            if not os.path.exists(resume_path):
                return render_page('文件保存失败，请重试。')

            # 保存申请信息
            db.session.add(JobApplication(
                job_id=selected_job_id,
                resume_filename=unique_filename,
                original_filename=resume_file.filename,
                **form
            ))
            db.session.commit()

            # 成功返回
            return render_template(
                'post-resume-zh.html',
                jobs=jobs,
                search=search,
                job_type=job_type,
                location=location,
                selected_job_id=None,
                selected_job=None,
                success_message=f'申请提交成功！您已成功申请 "{selected_job.title}" 职位，我们会尽快审核并与您联系。'
            )

        except Exception as e:
            db.session.rollback()
            if 'resume_path' in locals() and os.path.exists(resume_path):
                try:
                    os.remove(resume_path)
                except Exception:
                    pass
            print(f"Error in post_resume: {e}")
            import traceback; print(traceback.format_exc())
            return render_page('系统错误，请稍后重试。')

    return render_page()
@app.route('/admin/resumes')
@admin_required
def admin_resumes():
    """管理员简历预览界面"""
    # 获取筛选参数
    search = request.args.get('search', '')
    job_id = request.args.get('job_id', '', type=int)
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # 构建基础查询 - 使用正确的关联查询
    base_query = JobApplication.query.join(Job, JobApplication.job_id == Job.id).add_entity(Job)

    # 应用筛选条件
    if search:
        base_query = base_query.filter(
            db.or_(
                JobApplication.name.contains(search),
                JobApplication.email.contains(search),
                JobApplication.phone.contains(search),
                Job.title.contains(search)
            )
        )

    if job_id:
        base_query = base_query.filter(JobApplication.job_id == job_id)

    if status:
        base_query = base_query.filter(JobApplication.status == status)
    else:
        # 默认显示所有简历
        pass

    # 分页查询
    pagination = base_query.order_by(JobApplication.applied_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # 获取所有职位用于筛选
    jobs = Job.query.filter(Job.deadline >= datetime.utcnow()).all()

    # 统计信息 - 新简历对应 pending 状态
    total_count = JobApplication.query.count()
    pending_count = JobApplication.query.filter(
        db.or_(JobApplication.status.is_(None), JobApplication.status == 'pending')
    ).count()
    reviewed_count = JobApplication.query.filter_by(status='reviewed').count()
    contacted_count = JobApplication.query.filter_by(status='contacted').count()
    rejected_count = JobApplication.query.filter_by(status='rejected').count()
    hired_count = JobApplication.query.filter_by(status='hired').count()

    # 调试信息
    print(f"查询到的简历数量: {len(pagination.items)}")
    for item in pagination.items:
        print(f"简历: {item[0].name}, 职位: {item[1].title}, 状态: {item[0].status}")

    return render_template('admin-resumes.html',
                         resumes=pagination.items,
                         pagination=pagination,
                         jobs=jobs,
                         search=search,
                         selected_job_id=job_id,
                         selected_status=status,
                         total_count=total_count,
                         pending_count=pending_count,
                         reviewed_count=reviewed_count,
                         contacted_count=contacted_count,
                         rejected_count=rejected_count,
                         hired_count=hired_count)

@app.route('/admin/resume/<int:resume_id>')
@admin_required
def admin_resume_detail(resume_id):
    """简历详情页面"""
    resume_data = JobApplication.query.join(Job, JobApplication.job_id == Job.id)\
        .add_entity(Job)\
        .filter(JobApplication.id == resume_id)\
        .first_or_404()
    return render_template('admin-resume-detail.html', resume=resume_data)

@app.route('/admin/resume/<int:resume_id>/update-status', methods=['POST'])
@admin_required
def update_resume_status(resume_id):
    """更新简历状态"""
    resume = JobApplication.query.get_or_404(resume_id)
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')

    if new_status in ['pending', 'reviewed', 'contacted', 'rejected', 'hired']:
        resume.status = new_status
        if notes:
            # 如果需要保存备注，可以在这里添加备注字段
            pass

        db.session.commit()
        flash('简历状态已更新', 'success')
    else:
        flash('无效的状态', 'error')

    return redirect(url_for('admin_resume_detail', resume_id=resume_id))

@app.route('/admin/resume/<int:resume_id>/download')
@admin_required
def download_resume(resume_id):
    """下载简历文件"""
    resume = JobApplication.query.get_or_404(resume_id)

    if not resume.resume_filename:
        flash('简历文件不存在', 'error')
        return redirect(url_for('admin_resume_detail', resume_id=resume_id))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume.resume_filename)

    if not os.path.exists(file_path):
        flash('简历文件不存在', 'error')
        return redirect(url_for('admin_resume_detail', resume_id=resume_id))

    # 设置下载文件名
    download_name = f"{resume.name}_简历.{resume.resume_filename.rsplit('.', 1)[1].lower()}"

    return send_file(file_path, as_attachment=True, download_name=download_name)

@app.route('/admin/resume/<int:resume_id>/delete', methods=['POST'])
@admin_required
def delete_resume(resume_id):
    """删除简历"""
    resume = JobApplication.query.get_or_404(resume_id)

    # 删除文件
    if resume.resume_filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume.resume_filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(resume)
    db.session.commit()

    flash('简历已删除', 'success')
    return redirect(url_for('admin_resumes'))
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