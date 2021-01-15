# 1.导包
import json
from datetime import datetime

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import pymysql
import requests

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


# 中国疫情统计表
class China(db.Model):
    # 定义表名
    __tablename__ = "china"
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lastUpdateTime = db.Column(db.DateTime, unique=True)
    confirm = db.Column(db.Integer)
    suspect = db.Column(db.Integer)
    heal = db.Column(db.Integer)
    dead = db.Column(db.Integer)


# 地区疫情统计表
class Area(db.Model):
    # 定义表名
    __tablename__ = "area"
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lastUpdateTime = db.Column(db.DateTime, unique=True)
    city = db.Column(db.String(64))
    confirm = db.Column(db.Integer)
    suspect = db.Column(db.Integer)
    heal = db.Column(db.Integer)
    dead = db.Column(db.Integer)


# 知识表
class News(db.Model):
    # 定义表名
    __tablename__ = "news"
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, default=datetime.now)
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


# 爬虫接口数据
@app.route('/getReal', methods=['POST', 'GET'])
def getReal():
    if request.method == 'POST':
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (XHTML, like Gecko) '
                          'Chrome/73.0.3683.103 Safari/537.36 ',
            'Content-Type': 'application/json'
        }
        url = 'https://www.ncovchina.com/data/getDisease.html'
        res = requests.get(url, headers)
        # res.encoding = "utf-8"
        result = json.loads(res.text)
        if result['ret'] == 0:
            data = json.loads(result['data'])
            lastUpdateTime = data['lastUpdateTime']
            hasExist = China.query.filter(China.lastUpdateTime == lastUpdateTime).first()
            if hasExist:
                res = {
                    'op': 'success',
                    'data': data
                }
                return res
            else:
                confirm = data['chinaTotal']['confirm']
                suspect = data['chinaTotal']['suspect']
                heal = data['chinaTotal']['heal']
                dead = data['chinaTotal']['dead']
                info = China(lastUpdateTime=lastUpdateTime, confirm=confirm, suspect=suspect, heal=heal, dead=dead)
                db.session.add(info)
                db.session.commit()
                areaTotal = data['areaTree'][0]['children']
                for item in areaTotal:
                    city = item['name']
                    cityConfirm = item['total']['confirm']
                    citySuspect = item['total']['suspect']
                    cityHeal = item['total']['heal']
                    cityDead = item['total']['dead']
                    area = Area(lastUpdateTime=lastUpdateTime, city=city, confirm=cityConfirm, suspect=citySuspect, heal=cityHeal,
                                dead=cityDead)
                    db.session.add(area)
                    db.session.commit()
                res = {
                    'op': 'success',
                    'data': data
                }
                return res
        else:
            return
    else:
        return


@app.route('/')
def main():
    return '后台启动成功'


if __name__ == '__main__':
    app.run(debug=True)
