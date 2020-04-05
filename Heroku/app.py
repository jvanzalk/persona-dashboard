import os #Pull environmental variables from Heroku
from flask import Flask, render_template #Framework for building web application
import sqlalchemy #Connect and query sql db
from sqlalchemy import create_engine
import pandas as pd #Data manipulation

#To run locally:
# from config import dbuser, dbpwd, dbhost, dbport, dbname 

#Import config files from Heroku
dbuser = os.environ.get("dbuser")
dbpwd = os.environ.get("dbpwd")
dbhost = os.environ.get("dbhost")
dbport = os.environ.get("dbport")
dbname = os.environ.get("dbname")

#Configure Postgresql connection
engine = create_engine(f'postgresql://{dbuser}:{dbpwd}@{dbhost}:{dbport}/{dbname}')
conn = engine.connect()

#Initialize Flask application
app = Flask(__name__)

@app.route('/')
def index():
    #Reestablish DB connection
    conn = engine.connect()

    #Read in population table
    population = pd.read_sql("SELECT * FROM population", conn)
    #Convert to dictionary
    data = population.to_dict('records')

    #Avg engagement data
    avg_engage = pd.read_sql("SELECT * FROM avg_engage", conn)
    avg_engage = avg_engage.to_dict('records')

    #Engagement type breakdown
    engage_type = pd.read_sql("SELECT * FROM engage_type", conn)
    engage_type = engage_type.to_dict('records')

    #Engagement status
    recfreq = pd.read_sql("SELECT * FROM recfreq", conn)
    recfreq = recfreq.to_dict('records')

    #Population growth
    pop_growth = pd.read_sql("SELECT * FROM pop_growth", conn)
    
    #Create a dictionary with persona, y (# of contacts), and x (quarter)
    pop_growth = [{'persona':'Claire','y':pop_growth.loc[pop_growth.persona == 'Claire',].values.flatten().tolist()[1:],'x':list(pop_growth.columns)[1:]},
    {'persona':'Dan','y':pop_growth.loc[pop_growth.persona == 'Dan',].values.flatten().tolist()[1:],'x':list(pop_growth.columns)[1:]},
    {'persona':'Lynn','y':pop_growth.loc[pop_growth.persona == 'Lynn',].values.flatten().tolist()[1:],'x':list(pop_growth.columns)[1:]},
    {'persona':'Maya','y':pop_growth.loc[pop_growth.persona == 'Maya',].values.flatten().tolist()[1:],'x':list(pop_growth.columns)[1:]},
    {'persona':'Rey','y':pop_growth.loc[pop_growth.persona == 'Rey',].values.flatten().tolist()[1:],'x':list(pop_growth.columns)[1:]}]

    #Top items
    top_items = pd.read_sql("SELECT * FROM top_items", conn)
    top_items = top_items.to_dict('records')

    #Top campaigns
    top_campaigns = pd.read_sql("SELECT * FROM top_campaigns", conn)
    top_campaigns = top_campaigns.to_dict('records')
    
    #Make data accessible for plotting
    return render_template('index.html', data=data, avg_engage=avg_engage, engage_type=engage_type, recfreq=recfreq, pop_growth=pop_growth, top_campaigns=top_campaigns, top_items=top_items)

if __name__ == '__main__':
    app.run(debug=True)
