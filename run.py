from flask import Flask, render_template, request, session, redirect
from flask_session import Session
import pandas as pd
import utils
import datetime
import os


token = utils.getToken()
headers = {'Authorization' : f'Bearer {token}',
           'Content-Type' : 'application/json',
           'ConsistencyLevel' : 'eventual'}

app = Flask(__name__)
app.secret_key = 'tmp_key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = 86400
Session(app)

# Add Filter to Format Date in Jinja
@app.template_filter('formatdatetime')
def format_datetime(value, actual_format='%Y-%m-%dT%H:%M:%SZ', format="%d %b %Y %I:%M %p"):
    if value is None or str(value) == "":
        return ""
    return datetime.datetime.strptime(str(value), actual_format).strftime(format)

# Change Values of Remote Working Hours (SI)
@app.route('/modCompteur', methods=['POST'])
def modCompteur():
  compteur_path = "static/assets/data/Compteur.xlsx"
  df_compteur_data = pd.read_excel(compteur_path)
  
  if request.method == "POST":
    list_compteur = []
    for index in range(df_compteur_data.shape[0]):
      compteur = request.form.get(df_compteur_data['trg'][index])
      list_compteur.append(compteur)
  
    df_compteur_data["compteur"] = list_compteur
    df_compteur_data.to_excel(compteur_path, index=False)
  return redirect(session['url'])

# Add Absence (SI)
@app.route('/addAbsences', methods=['POST'])
def addAbsences():
  absences_path = "static/assets/data/absences.xlsx"
  df_absences_data = pd.read_excel(absences_path)
  
  if request.method == "POST":
    list_new_absences = []
    trg = request.form.get("trg")
    date = request.form.get("daterange")
    dateDebut = date.split("-")[0]
    dateFin = date.split("-")[1]
    list_new_absences.append([trg, dateDebut, dateFin])
    df_new_absences = pd.DataFrame(list_new_absences)
    df_new_absences.columns = ["trg","dateDebut","dateFin"]
    
    df_absences_data = pd.concat([df_absences_data, df_new_absences])
    df_absences_data.to_excel(absences_path, index=False)
    
    utils.SI.getDatasetsGraphAbsences()
  return redirect(session['url'])

# Add Informal Talks (SI) SIMPLE TABLE
@app.route('/addCauserie', methods=['POST'])
def addCauserie():
  causeries_path = "static/assets/data/causeries.pkl"
  df_causeries_data = pd.read_pickle(causeries_path)
  
  if request.method == "POST":
    list_informal_talks = []
    month = request.form.get("month")
    scholarYear = request.form.get("scholarYear")
    subject = request.form.get("subject")
    date = ""
    list_informal_talks.append([scholarYear, month, subject, date])
    list_informal_talks = pd.DataFrame(list_informal_talks)
    list_informal_talks.columns = ["annee","mois","theme","date"]
    df_causeries_data = pd.concat([df_causeries_data, list_informal_talks],ignore_index=True)
    df_causeries_data.to_pickle(causeries_path)
    
    utils.SI.getDatasetsGraphAbsences()
  return redirect(session['url'])

# Add Date to Informal Talks (SI) SIMPLE TABLE
@app.route('/addDateTable/<index>/<date>', methods=['POST'])
def addDateTable(index, date):
  causeries_path = "static/assets/data/causeries.pkl"
  if date == "undefined":
    date = ""
  df_causeries_data = pd.read_pickle(causeries_path)
  df_causeries_data.loc[int(index), 'date'] = date
  df_causeries_data.to_pickle(causeries_path)
  
  return redirect(session['url'])

# Add Date to Informal Talks (SI) COMPLEX DISPLAY
@app.route('/addDate/<sheet_index>/<index_in_sheet>/<date>', methods=['POST'])
def addDate(sheet_index, index_in_sheet, date):
  causeries_path = "static/assets/data/causeries.xlsx"
  if date == "undefined":
    date = ""
    
  xls = pd.ExcelFile(causeries_path)
  dict_sheet = {}
  for sheet_name in xls.sheet_names:
      dict_sheet[sheet_name] = xls.parse(sheet_name, usecols=[1,2,3])

  with pd.ExcelWriter(causeries_path) as writer:
    for index in range(len(dict_sheet)):
        df_sheet = dict_sheet[list(dict_sheet)[index]]
        if index == int(sheet_index):
            df_sheet.loc[int(index_in_sheet), 'date'] = date

        df_sheet.to_excel(writer, sheet_name=str(list(dict_sheet)[index]))
  
  return redirect(session['url'])

# Add Subject to Informal Talks (SI) COMPLEX DISPLAY
@app.route('/addTheme/<sheet_index>/<index_in_sheet>/<theme>', methods=['POST'])
def addTheme(sheet_index, index_in_sheet, theme):
  causeries_path = "static/assets/data/causeries.xlsx"
  if theme == "undefined":
    theme = ""
    
  xls = pd.ExcelFile(causeries_path)
  dict_sheet = {}
  for sheet_name in xls.sheet_names:
      dict_sheet[sheet_name] = xls.parse(sheet_name, usecols=[1,2,3])

  with pd.ExcelWriter(causeries_path) as writer:
    for index in range(len(dict_sheet)):
        df_sheet = dict_sheet[list(dict_sheet)[index]]
        if index == int(sheet_index):
            df_sheet.loc[int(index_in_sheet), 'theme'] = theme

        df_sheet.to_excel(writer, sheet_name=str(list(dict_sheet)[index]))
  
  return redirect(session['url'])

# Remove Absence (SI)
@app.route('/removeAbsence/<index>')
def removeAbsence(index):
  absences_path = "static/assets/data/absences.xlsx"
  df_absences_data = pd.read_excel(absences_path)
  df_absences_data = df_absences_data.drop(int(index), axis=0).reset_index(drop=True)
  df_absences_data.to_excel(absences_path, index=False)
  
  utils.SI.getDatasetsGraphAbsences()
  return redirect(session['url'])

# Groups' Page
@app.route('/groupes')
def groupes():

    session['url'] = request.url
    
    group_path = "static/assets/data/groupTable.pkl"
    df_group_data = pd.read_pickle(group_path)
    lastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(group_path)).strftime("%d/%m/%Y %H:%M:%S")
    
    return render_template('groupes.html', 
                           
                           df_group_data=df_group_data,
                           
                           lastUpdate=lastUpdate)

# Users' Page
@app.route('/users')
def users():

    session['url'] = request.url
    
    user_path = "static/assets/data/userTable.pkl"
    df_user_data = pd.read_pickle(user_path)

    onedrive_path = "static/assets/data/onedriveTable.pkl"
    df_onedrive_data = pd.read_pickle(onedrive_path)
    
    lastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(user_path)).strftime("%d/%m/%Y %H:%M:%S")
    
    return render_template('users.html', 
                           df_user_data=df_user_data,
                           df_onedrive_data=df_onedrive_data,
                          
                           lastUpdate=lastUpdate)

# SI Page
@app.route('/si')
def si():
  
  session['url'] = request.url
  
  compteur_path = "static/assets/data/Compteur.xlsx"
  df_compteur_data = pd.read_excel(compteur_path)
  
  license_path = "static/assets/data/licenseTable.pkl"
  df_license_data = pd.read_pickle(license_path)
  
  absences_path = "static/assets/data/absences.xlsx"
  df_absences_data = pd.read_excel(absences_path)
  
  causeries_path = "static/assets/data/causeries.xlsx"
  xls = pd.ExcelFile(causeries_path)
  dict_causeries = {}
  for sheet_name in xls.sheet_names:
      dict_causeries[sheet_name] = xls.parse(sheet_name).fillna("")
  now = datetime.datetime.now()
  month = now.month
  year = now.year
  if month < 9:
      scholar_year = f"Septembre{year-1}"
  else:
      scholar_year = f"Septembre{year}"
      
  causeriesTable_path = "static/assets/data/causeries.pkl"
  df_causerieTable_data = pd.read_pickle(causeriesTable_path)
  
  mails_path = "static/assets/data/MailsTable.pkl"
  df_mails_data = pd.read_pickle(mails_path)
  df_mails_data = df_mails_data.loc[df_mails_data["userPrincipalName"].str.contains("utilisateur_56@formation-industries-ese.fr") | 
                              df_mails_data["userPrincipalName"].str.contains("utilisateur_191@formation-industries-ese.fr") |
                              df_mails_data["userPrincipalName"].str.contains("utilisateur_30@formation-industries-ese.fr") |
                              df_mails_data["userPrincipalName"].str.contains("utilisateur_547@formation-industries-ese.fr") |
                              df_mails_data["userPrincipalName"].str.contains("utilisateur_206@formation-industries-ese.fr") ].reset_index(drop=True)
  
  compteurlastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(compteur_path)).strftime("%d/%m/%Y %H:%M:%S")
  absenceslastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(absences_path)).strftime("%d/%m/%Y %H:%M:%S")
  mailslastUpdate = datetime.datetime.strptime(str(df_mails_data['Report Refresh Date'][0]), "%Y-%m-%d").strftime("%d/%m/%Y")
  
  if not df_absences_data.empty:
      date_today = pd.to_datetime(datetime.datetime.now().date())
      df_absences_data[['dateFin', 'dateDebut']] = df_absences_data[['dateFin', 'dateDebut']].apply(pd.to_datetime, dayfirst=True)

      df_absences_data['Is Past'] = df_absences_data['dateFin'] < date_today
      df_absences_data = df_absences_data[df_absences_data['Is Past'] == False ].reset_index()

      df_absences_data['dateFin'] += pd.Timedelta(days=1)

      df_absences_data['In Progress'] = (df_absences_data['dateDebut'] <= date_today) & (df_absences_data['dateFin'] >= date_today)

      df_absences_data['Starts In'] = (df_absences_data['dateDebut'][~df_absences_data['Is Past']] - date_today).dt.days
      df_absences_data['Starts In'] = df_absences_data['Starts In'].fillna(0).astype(int)
      df_absences_data['Ends In'] = (df_absences_data['dateFin'][~df_absences_data['Is Past']] - date_today).dt.days
      df_absences_data['Ends In'] = df_absences_data['Ends In'].fillna(0).astype(int)

      df_absences_data['dateFin'] -= pd.Timedelta(days=1)
      
  datasetsGraphAbsences_path = "static/assets/data/datasetsGraphAbsences.pkl"
  df_datasets_absences = pd.read_pickle(datasetsGraphAbsences_path)
  
  return render_template('si.html', 
                          df_compteur_data=df_compteur_data,
                          df_absences_data=df_absences_data,
                          df_mails_data=df_mails_data,
                          df_license_data=df_license_data,
                          dict_causeries=dict_causeries,
                          df_causerieTable_data=df_causerieTable_data,
                          df_datasets_absences=df_datasets_absences,
                          
                          scholar_year=scholar_year,
                          
                          compteurlastUpdate=compteurlastUpdate,
                          absenceslastUpdate=absenceslastUpdate,
                          mailslastUpdate=mailslastUpdate)

# Update Groups' Data
@app.route('/groupUpdate')
def groupUpdate():
    utils.Users.getListUsers()
    utils.Group.getGroupsTable()
    return redirect(session['url'])

# Update Users' Data
@app.route('/userUpdate')
def userUpdate():
    utils.Users.getListUsers()
    utils.Mail.getMailInfo()
    utils.Users.getOneDrive()
    return redirect(session['url'])

# Keep Tab Dashboard in Memory
@app.route('/getActualTab/<data>', methods=['POST'])
def getActualTab(data):
  if request.method == "POST":
    session['tab'] = data
  return ('/')

# Index Page
@app.route('/')
def index():
  
  session['connectedUser'] = utils.Users.getConnectedUser() # Should Be Called At Login
  session['url'] = request.url
  
  if not session.get('tab'):
    session['tab'] = "groupes"
  
  user_path = "static/assets/data/userTable.pkl"
  df_user_data = pd.read_pickle(user_path)
  userLastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(user_path)).strftime("%d/%m/%Y %H:%M:%S")
  
  mails_path = "static/assets/data/MailsTable.pkl"
  df_mails_data = pd.read_pickle(mails_path)
    
  group_path = "static/assets/data/groupTable.pkl"
  df_group_data = pd.read_pickle(group_path)
  groupLastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(group_path)).strftime("%d/%m/%Y %H:%M:%S")
  
  compteur_path = "static/assets/data/Compteur.xlsx"
  df_compteur_data = pd.read_excel(compteur_path)
  
  absences_path = "static/assets/data/absences.xlsx"
  df_absences_data = pd.read_excel(absences_path)
  
  datasetsGraphAbsences_path = "static/assets/data/datasetsGraphAbsences.pkl"
  df_dataset_final = pd.read_pickle(datasetsGraphAbsences_path)
  
  df_mailsSI_data = df_mails_data.loc[df_mails_data["userPrincipalName"].str.contains("utilisateur_56@formation-industries-ese.fr") | 
                              df_mails_data["userPrincipalName"].str.contains("utilisateur_191@formation-industries-ese.fr") |
                              df_mails_data["userPrincipalName"].str.contains("utilisateur_30@formation-industries-ese.fr") |
                              df_mails_data["userPrincipalName"].str.contains("utilisateur_547@formation-industries-ese.fr") |
                              df_mails_data["userPrincipalName"].str.contains("utilisateur_206@formation-industries-ese.fr") ].reset_index(drop=True)
  
  compteurlastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(compteur_path)).strftime("%d/%m/%Y %H:%M:%S")
  absenceslastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(absences_path)).strftime("%d/%m/%Y %H:%M:%S")
  mailslastUpdate = datetime.datetime.strptime(str(df_mails_data['Report Refresh Date'][0]), "%Y-%m-%d").strftime("%d/%m/%Y")
  
  if not df_absences_data.empty:
      date_today = pd.to_datetime(datetime.datetime.now().date())
      df_absences_data[['dateFin', 'dateDebut']] = df_absences_data[['dateFin', 'dateDebut']].apply(pd.to_datetime, dayfirst=True)

      df_absences_data['Is Past'] = df_absences_data['dateFin'] < date_today
      df_absences_data = df_absences_data[df_absences_data['Is Past'] == False ].reset_index()

      df_absences_data['dateFin'] += pd.Timedelta(days=1)

      df_absences_data['In Progress'] = (df_absences_data['dateDebut'] <= date_today) & (df_absences_data['dateFin'] >= date_today)

      df_absences_data['Starts In'] = (df_absences_data['dateDebut'][~df_absences_data['Is Past']] - date_today).dt.days
      df_absences_data['Starts In'] = df_absences_data['Starts In'].fillna(0).astype(int)
      df_absences_data['Ends In'] = (df_absences_data['dateFin'][~df_absences_data['Is Past']] - date_today).dt.days
      df_absences_data['Ends In'] = df_absences_data['Ends In'].fillna(0).astype(int)

      df_absences_data['dateFin'] -= pd.Timedelta(days=1)
  
  return render_template('index.html', 
                          df_group_data=df_group_data,
                          df_user_data=df_user_data,
                          df_mails_data=df_mails_data,
                          df_mailsSI_data=df_mailsSI_data,
                          df_compteur_data=df_compteur_data,
                          df_absences_data=df_absences_data,
                          df_datasets_absences=df_dataset_final,
                          
                          groupLastUpdate=groupLastUpdate,
                          userLastUpdate=userLastUpdate,
                          compteurlastUpdate=compteurlastUpdate,
                          absenceslastUpdate=absenceslastUpdate,
                          mailslastUpdate=mailslastUpdate,
                          
                          tab=session['tab'])



# Errors
@app.errorhandler(404)
def not_found(e):
  return render_template('404.html'), 404
@app.errorhandler(401)
def denied(e):
  return render_template('401.html'), 401
@app.errorhandler(500)
def internal_server_error(e):
  return render_template('500.html'), 500

# Launch App Server
if __name__ == '__main__':
  app.run(debug=True)
