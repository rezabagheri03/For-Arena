"""
Backend Server for Personal Resume Website
سرور بک‌اند برای وبسایت رزومه شخصی
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os
import logging

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# مسیر پایه پروژه
basedir = os.path.abspath(os.path.dirname(__file__))

# تنظیمات دیتابیس SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'resume.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ---------- مدل‌های دیتابیس ----------
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_read = db.Column(db.Boolean, default=False)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200))            # عنوان انگلیسی
    description = db.Column(db.Text)
    description_en = db.Column(db.Text)             # توضیح انگلیسی
    technologies = db.Column(db.String(300))
    technologies_en = db.Column(db.String(300))     # تکنولوژی‌های انگلیسی
    link = db.Column(db.String(300))
    order = db.Column(db.Integer, default=0)
    images = db.relationship('ProjectImage', backref='project', lazy=True, cascade="all, delete-orphan")


class ProjectImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(300), nullable=False)  # مسیر نسبی داخل static: e.g., "projects/resume1.jpg"
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    order = db.Column(db.Integer, default=0)


# ---------- مسیرهای اصلی ----------
@app.route('/')
def index():
    """صفحه اصلی - نمایش رزومه با پروژه‌ها و عکس‌هایشان"""
    projects = Project.query.order_by(Project.order).all()
    return render_template('index.html', projects=projects)


@app.route('/api/contact', methods=['POST'])
def contact():
    """دریافت و ذخیره پیام تماس"""
    try:
        data = request.get_json()

        # اعتبارسنجی فیلدهای ضروری
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if field not in data or not data[field].strip():
                msg = f'فیلد {field} الزامی است' if request.headers.get('Accept-Language', 'fa') == 'fa' else f'Field {field} is required'
                return jsonify({'success': False, 'message': msg}), 400

        # اعتبارسنجی ایمیل
        email = data['email'].strip()
        if '@' not in email or '.' not in email.split('@')[1]:
            msg = 'ایمیل معتبر نیست' if request.headers.get('Accept-Language', 'fa') == 'fa' else 'Invalid email address'
            return jsonify({'success': False, 'message': msg}), 400

        # ساخت و ذخیره پیام
        new_message = ContactMessage(
            name=data['name'].strip(),
            email=email,
            phone=data.get('phone', '').strip(),
            message=data['message'].strip()
        )
        db.session.add(new_message)
        db.session.commit()

        logger.info(f"پیام جدید از {email} ذخیره شد")

        return jsonify({
            'success': True,
            'message': 'پیام شما با موفقیت ارسال شد. به زودی با شما تماس خواهم گرفت.' if request.headers.get('Accept-Language', 'fa') == 'fa' else 'Your message has been sent successfully. I will contact you soon.'
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"خطا در ذخیره پیام: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطای سرور. لطفاً دوباره تلاش کنید.' if request.headers.get('Accept-Language', 'fa') == 'fa' else 'Server error. Please try again.'
        }), 500


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """مشاهده پیام‌های ذخیره شده (با احراز هویت ساده)"""
    password = request.args.get('password')
    if password != 'admin123':
        return jsonify({'success': False, 'message': 'دسترسی غیرمجاز'}), 401

    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    result = [{
        'id': m.id, 'name': m.name, 'email': m.email,
        'phone': m.phone, 'message': m.message,
        'created_at': m.created_at.isoformat(), 'is_read': m.is_read
    } for m in messages]
    return jsonify({'success': True, 'contacts': result, 'count': len(result)}), 200


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()}), 200


# ---------- ساخت جداول و داده‌های اولیه ----------
with app.app_context():
    db.create_all()

    if Project.query.count() == 0:
        # پروژه اول
        proj1 = Project(
            title="وبسایت رزومه داینامیک",
            description="همین پروژه؛ یک وب‌سایت مدرن با Flask و SQLAlchemy و Swiper.js",
            technologies="Python, Flask, SQLAlchemy, Swiper.js",
            link="https://github.com/alirezamojaveri/resume",
            order=1
        )
        proj1.images = [
            ProjectImage(image="projects/resume1.jpg", order=1),
            ProjectImage(image="projects/resume2.jpg", order=2),
            ProjectImage(image="projects/resume3.jpg", order=3)
        ]

        # پروژه دوم
        proj2 = Project(
            title="اسکنر امنیتی شبکه",
            description="اسکنر پورت و آسیب‌پذیری با پایتون و کتابخانه Scapy",
            technologies="Python, Scapy, Network",
            link="https://github.com/alirezamojaveri/net-scanner",
            order=2
        )
        proj2.images = [
            ProjectImage(image="projects/scanner1.jpg", order=1),
            ProjectImage(image="projects/scanner2.jpg", order=2)
        ]

        # پروژه سوم
        proj3 = Project(
            title="سیستم مدیریت محتوا",
            description="پنل ادمین با Django و رابط کاربری React",
            technologies="Python, Django, React, REST API",
            link="https://github.com/alirezamojaveri/cms",
            order=3
        )
        proj3.images = [
            ProjectImage(image="projects/cms1.jpg", order=1),
            ProjectImage(image="projects/cms2.jpg", order=2),
            ProjectImage(image="projects/cms3.jpg", order=3)
        ]

        db.session.add_all([proj1, proj2, proj3])
        db.session.commit()
        logger.info("پروژه‌های نمونه با عکس‌هایشان اضافه شدند.")


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    logger.info(f"سرور روی http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)