from flask import Flask,render_template, g, request

from datetime import datetime
from db import connect_db, get_db

app = Flask(__name__)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite3_db.close()


#VIEWS
@app.route('/', methods = ['GET','POST'])
def index():
    db = get_db()

    if request.method == 'POST':
        date = request.form.get('date')
        date_time = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(date_time,'%Y%m%d')

        db.execute('insert into log_date (entry_date) values (?)',[database_date])
        db.commit()

    cur = db.execute('select log_date.entry_date,sum(food.protein) as protein,sum(food.carbohydrates) as carbohydrates,sum(food.fat) as fat,sum(food.calories)as calories from log_date join food_date on food_date.log_date_id=log_date.id join food on food.id=food_date.food_id group by log_date.id order by log_date.entry_date desc')
    results = cur.fetchall()

    date_results = []


    for item in results:
        single_date = {}

        single_date['entry_date']  = item['entry_date']
        single_date['protein'] = item['protein']
        single_date['carbohydrates'] = item['carbohydrates']
        single_date['fat'] = item['fat']
        single_date['calories'] = item['calories']

        d = datetime.strptime(str(item['entry_date']), '%Y%m%d')
        single_date['pretty_date'] = datetime.strftime(d,'%B %d, %Y')

        date_results.append(single_date)


    return render_template('home.html', results=date_results)

@app.route('/view/<date>', methods=['GET','POST']) #date to look like 20200523
def view(date):
    db = get_db()

    cur = db.execute('select id, entry_date from log_date where entry_date = ?',[date])
    date_result = cur.fetchone()

    if request.method == 'POST':
        #return 'The food item select is {}'.format(request.form['food-select'])
        db.execute('insert into food_date (food_id, log_date_id) values (?,?)', [request.form.get('food-select'),date_result['id']])
        db.commit()

    #putting dates on the form
    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d,'%B %d, %Y')

    #populating form with food info
    food_cur = db.execute('select id, name from food')
    food_results = food_cur.fetchall()

    log_cur = db.execute('''select food.name, food.protein, food.carbohydrates, food.fat, food.calories
    from log_date
    join food_date on food_date.log_date_id = log_date.id
    join food on food.id = food_date.food_id
    where log_date.entry_date=?''',[date])

    #food_date.food_id, food_date.log_date_id
    #join food_date on food_date.log_date_id = log_date.id


    log_results = log_cur.fetchall()

    totals = {}
    totals['protein'] = 0
    totals['carbohydrates'] = 0
    totals['fat'] = 0
    totals['calories'] = 0

    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']


    return render_template('day.html', entry_date=date_result['entry_date'],  pretty_date=pretty_date, food_results=food_results, log_results=log_results, totals=totals)

@app.route('/food', methods=['GET','POST'])
def food():
    db = get_db()

    if request.method == 'POST':
        name = request.form.get('food-name')
        protein = int(request.form.get('protein'))
        carbohydrates = int(request.form.get('carbohydrates'))
        fat = int(request.form.get('fat'))

        calories = protein*4 + carbohydrates*4 + fat*9

        db.execute('insert into food (name, protein, carbohydrates, fat, calories) values (?,?,?,?,?)', [name,protein,carbohydrates,fat,calories])
        db.commit()

    cur = db.execute('select name,protein, carbohydrates, fat, calories from food')

    result = cur.fetchall()

    return render_template('add_food.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
