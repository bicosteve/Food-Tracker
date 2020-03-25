create table log_date(
    id integer primary key autoincrement,
    entry_date date not null
);


create table food(
    id integer primary key autoincrement,
    name text not null,
    protein integer not null,
    carbohydrates integer not null,
    fat integer not null,
    calories integer not null
);


create table food_date(
    food_id integer not null,
    log_date_id integer not null,
    primary key (food_id,log_date_id)
);


log_cur = db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories
    from  log_date
    join food_date on food_date.log_date_id = log_date.id
    join food on food.id = food_date.food_id
    where log_date.entry_date=?',[date])


food_date.food_id, food_date.log_date_id
