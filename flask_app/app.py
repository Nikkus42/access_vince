from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, Boolean, Date, MetaData
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from datetime import date
import os
import hashlib
from dotenv import load_dotenv
load_dotenv()

# Test des variables d'environnement
print("AUTH_POSTGRES_USER:", os.getenv('AUTH_POSTGRES_USER'))
print("AUTH_POSTGRES_PASSWORD:", os.getenv('AUTH_POSTGRES_PASSWORD'))
print("AUTH_POSTGRES_DB:", os.getenv('AUTH_POSTGRES_DB'))
print("AUTH_POSTGRES_HOST:", os.getenv('AUTH_POSTGRES_HOST'))
print("AUTH_POSTGRES_PORT:", os.getenv('AUTH_POSTGRES_PORT'))

app = Flask(__name__)

# Configuration pour la base de données access_leg_db
app.config['SQLALCHEMY_DATABASE_URI_ACCESS_LEG'] = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

auth_postgres_password = quote_plus(os.getenv('AUTH_POSTGRES_PASSWORD'))

# Configuration pour la base de données authent_leg_db
app.config['SQLALCHEMY_DATABASE_URI_AUTHENT_LEG'] = (
    f"postgresql+psycopg2://{os.getenv('AUTH_POSTGRES_USER')}:{auth_postgres_password}"
    f"@{os.getenv('AUTH_POSTGRES_HOST')}:{os.getenv('AUTH_POSTGRES_PORT')}/{os.getenv('AUTH_POSTGRES_DB')}"
)

# Ajout du print ici pour vérifier l'URI générée
print("URI AUTHENT_LEG :", app.config['SQLALCHEMY_DATABASE_URI_AUTHENT_LEG'])

# Initialisation des connexions aux bases de données
engine_access_leg = create_engine(app.config['SQLALCHEMY_DATABASE_URI_ACCESS_LEG'])
engine_authent_leg = create_engine(app.config['SQLALCHEMY_DATABASE_URI_AUTHENT_LEG'])

metadata = MetaData()

# Définir la table user
user_table = Table(
    'user', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('utilisateur', String(255)),
    Column('pwd', String(255)),
    Column('type', String(10)),
    Column('date_creat_pwd', Date),
    Column('validation', Boolean, default=False)
)


@app.route('/cartographie_interne')
def cartographie_interne():
    return render_template('cartographie_interne.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/logging.html')
def logging():
    return render_template('logging.html')

@app.route('/logging_new.html')
def logging_new():
    return render_template('logging_new.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    email = request.form['email']
    password = request.form['password']

    # Vérification du type d'utilisateur
    user_type = 'interne' if email.endswith('@leg.fr') else 'externe'

    # Hashage SHA-256 répété 10 fois
    hashed_email = email
    for _ in range(10):
        hashed_email = hashlib.sha256(hashed_email.encode()).hexdigest()

    hashed_password = password
    for _ in range(10):
        hashed_password = hashlib.sha256(hashed_password.encode()).hexdigest()

    # Insertion dans la base de données
    with engine_authent_leg.connect() as connection:
        connection.execute(user_table.insert().values(
            utilisateur=hashed_email,
            pwd=hashed_password,
            type=user_type,
            date_creat_pwd=date.today(),
            validation=False
        ))
    
    # Une fois terminé, rediriger vers une page HTML
    return redirect(url_for('success_page'))  # Redirige vers une autre route

@app.route('/success')
def success_page():
    return render_template('logging.html')  # Affiche une page HTML





# Créer des sessions pour interagir avec les bases de données
#SessionAccessLeg = sessionmaker(bind=engine_access_leg)
#SessionAuthentLeg = sessionmaker(bind=engine_authent_leg)

#@app.route('/data_from_access_leg')
#def data_from_access_leg():
#    session = SessionAccessLeg()
#    # Exécutez vos requêtes ici
#    result = session.execute("SELECT * FROM your_table")
#    data = result.fetchall()
#    session.close()
#    return str(data)

#@app.route('/data_from_authent_leg')
#def data_from_authent_leg():
#    session = SessionAuthentLeg()
    # Exécutez vos requêtes ici
#    result = session.execute("SELECT * FROM your_auth_table")
#    data = result.fetchall()
#    session.close()
#    return str(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

    