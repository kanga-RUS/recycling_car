#-*- coding: utf-8 -*-
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flask_wtf import Form
from wtforms.fields.html5 import DateField
from wtforms import StringField
from wtforms.validators import Regexp, InputRequired
from datetime import datetime

project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, './templates')
app = Flask(__name__, template_folder=template_path)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vin = db.Column(db.String(17), unique=True)
    start_date = db.Column(db.Date, nullable=False)
    stop_date = db.Column(db.Date, nullable=False)
    ptc = db.Column(db.String(255), nullable=False)


class AddCarForm(Form):
    vin = StringField(
        u'VIN номер',
        validators=[
            InputRequired(),
            Regexp(
                '^[A-HJ-NPR-Za-hj-npr-z\d]{8}[\dX][A-HJ-NPR-Za-hj-npr-z\d]{2}\d{6}$',
                message=u'VIN номер должен состоять из 17 цифр и букв латинского алфавита (за исключением: I, O, Q, 0, 1)'
            )
        ]
    )
    start_date = DateField(
        u'Дата выпуска автомобиля',
        validators=[InputRequired(),]
    )
    stop_date = DateField(
        u'Дата утилизации автомобиля',
        validators=[InputRequired()]
    )

    def validate(self):
        if not super(AddCarForm, self).validate():
            return False
        if db.session.query(Car).filter(Car.vin == self.vin.data).first() is not None:
            msg = u'Такой VIN номер уже есть в базе'
            self.vin.errors.append(msg)
            return False
        if self.stop_date.data == self.start_date.data:
            msg = u'Даты не могут совпадать!'
            self.stop_date.errors.append(msg)
            return False
        elif self.stop_date.data < self.start_date.data:
            msg = u'Дата утилизации не может быть раньше даты выпуска!'
            self.stop_date.errors.append(msg)
            return False
        return True


class GetInfoForm(Form):
    start_date = DateField(
        u'Дата начала периода',
        validators=[InputRequired()]
    )
    stop_date = DateField(
        u'Дата окончания периода',
        validators=[InputRequired()]
    )

    def validate(self):
        if not super(GetInfoForm, self).validate():
            return False
        if self.stop_date.data == self.start_date.data:
            msg = u'Даты не могут совпадать!'
            self.stop_date.errors.append(msg)
            return False
        elif self.stop_date.data < self.start_date.data:
            msg = u'Дата окончания периода не может быть раньше даты начала периода!'
            self.stop_date.errors.append(msg)
            return False
        return True


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    form = AddCarForm()
    if request.method == 'POST' and form.validate_on_submit():
        if request.files['file'] and allowed_file(request.files['file'].filename):
            file = request.files['file']
            filename = form.vin.data + '.{}'.format(file.filename.split('.')[-1])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            car = Car(
                vin=form.vin.data,
                start_date=form.start_date.data,
                stop_date=form.stop_date.data,
                ptc=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            )
            db.session.add(car)
            db.session.commit()
            flash(u'Информация успешно добавлена в базу данных')
            return redirect('add_car')
    return render_template('add_car.html', form=form)


@app.route('/get_info', methods=['GET', 'POST'])
def get_info():
    form = GetInfoForm()
    if request.method == 'POST' and form.validate_on_submit():
        start_date = form.start_date.data
        stop_date = form.stop_date.data
        return redirect(url_for('search_results', start_date=start_date, stop_date=stop_date))
    return render_template('get_info.html', form=form)


@app.route('/search_results')
def search_results():
    page = request.args.get('page', 1, type=int)
    cars = db.session.query(Car).filter(
        ((request.args.get('start_date') - Car.stop_date) * (request.args.get('stop_date') - Car.start_date)) <= 0
    ).paginate(page=page, per_page=3)
    return render_template('search_results.html', cars=cars, dates=request.args)



if __name__ == "__main__":
    app.run()
