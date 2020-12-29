# 1.导包
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import pymysql

pymysql.install_as_MySQLdb()
# 2.创建flask应用对象
app = Flask(__name__)


# 跨域支持
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


app.after_request(after_request)
# 3.配置sqlalchemy的参数
# 4.将参数传入flask对象
app.config.from_pyfile('config.py')

# 5.利用SQLAlchemy中传入app参数实例化Flask对象
db = SQLAlchemy(app)
ma = Marshmallow(app)


# 6.创建数据库模型制作表
# 用户表
class User(db.Model):
    # 定义表名
    __tablename__ = "user"
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))


# 知识表
class News(db.Model):
    # 定义表名
    __tablename__ = "news"
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(256))
    title = db.Column(db.String(256), unique=True)
    content = db.Column(db.String(256))


class NewsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = News


# 登录
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter(User.name == username, User.password == password).first()
        if user:
            res = {
                'op': 'success',
            }
            return res
        else:
            res = {
                'op': 'fail',
                'message': '账号密码错误'
            }
            return res
    else:
        return


# 添加数据
@app.route('/addNews', methods=['POST', 'GET'])
def addNews():
    if request.method == 'POST':
        type_ = request.form['type']
        title = request.form['title']
        content = request.form['content']
        info = News(type=type_, title=title, content=content)
        print(info)
        db.session.add(info)
        db.session.commit()
        res = {
            'op': 'success',
        }
        return res
    else:
        return


# 删除数据
@app.route('/deleteNews', methods=['POST', 'GET'])
def deleteNews():
    if request.method == 'POST':
        id_ = request.form['id']
        type_ = request.form['type']
        news = News.query.filter(News.id == id_, News.type == type_).first()
        db.session.delete(news)
        db.session.commit()
        res = {
            'op': 'success',
        }
        return res
    else:
        return


# 修改数据
@app.route('/editNews', methods=['POST', 'GET'])
def editNews():
    if request.method == 'POST':
        id_ = request.form['id']
        type_ = request.form['type']
        title = request.form['title']
        content = request.form['content']
        news = News.query.filter(News.id == id_, News.type == type_).first()
        news.title = title
        news.content = content
        db.session.commit()
        res = {
            'op': 'success',
        }
        return res
    else:
        return


# 获取数据
@app.route('/getNews', methods=['POST', 'GET'])
def getNews():
    if request.method == 'POST':
        type_ = request.form['type']
        news = News.query.filter(News.type == type_).all()
        news_schema = NewsSchema(many=True)
        news_data = news_schema.dump(news)
        res = {
            'op': 'success',
            'data': eval(str(news_data))
        }
        return res
    else:
        return


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
