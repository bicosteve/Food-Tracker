from flask import Flask,render_template,g,request
import sqlite3
from datetime import datetime



app = Flask(__name__)

#db helpers connection
def connect_db():
    sql = sqlite3.connect('food_log.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g,'sqlite3'):
        g.sqlite3_db = connect_db()
    return g.sqlite3_db

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

    cur = db.execute('select entry_date from log_date order by entry_date desc')
    results = cur.fetchall()

    neat_results = []

    for item in results:
        single_date = {}

        d = datetime.strptime(str(item['entry_date']), '%Y%m%d')
        single_date['entry_date'] = datetime.strftime(d,'%B %d, %Y')

        neat_results.append(single_date)


    return render_template('home.html', results=neat_results)

@app.route('/view')
def view():
    return render_template('day.html')

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
