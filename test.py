#%%
import base64
from io import StringIO
import json
import math
import os
from IPython.display import display
import pandas as pd
import requests
import datetime
import utils
from math import isnan
from hurry.filesize import size

token = utils.getToken()
headers = {'Authorization' : f'Bearer {token}',
           'Content-Type' : 'application/json',
           'ConsistencyLevel' : 'eventual'}



# Test token validity
#%%
request = requests.get('https://graph.microsoft.com/v1.0/', headers=headers)
if request.status_code == 401:
    print("Expired Token")
else:
    print("Valid Token")


# Show Users
#%%
request = requests.get('https://graph.microsoft.com/v1.0/users/', headers=headers)
df = pd.json_normalize(request.json(), record_path=['value'])

display(df)


# Show total mail for user
# %%
request = requests.get('https://graph.microsoft.com/v1.0/me/mailFolders', headers=headers)
personal_mails_data = pd.json_normalize(request.json(), record_path=['value'])
nbMail = personal_mails_data['totalItemCount'].sum()
print(nbMail)

# test groups
# %%
request = requests.get("https://graph.microsoft.com/v1.0/groups?$count=true", headers=headers)
df = pd.json_normalize(request.json())
display(df)
# idGroups = df['id']
# for idGroup in idGroups:
#     request = requests.get(f"https://graph.microsoft.com/v1.0/groups/{idGroup}", headers=headers)
#     df1 = pd.json_normalize(request.json())
#     # display(df1)

# %%
date_value = datetime.today().strftime("%d/%m/%Y %H:%M:%S")
print(date_value)

# %%
date_value = datetime.today().strftime('%Y-%m-%d')
request = requests.get(f"https://graph.microsoft.com/v1.0/reports/getOffice365GroupsActivityDetail(period='D180')", headers=headers)
csv = request.content.decode("utf-8")
df = pd.read_csv(StringIO(csv), sep=",")
display(df)
# %%
request = requests.get('https://graph.microsoft.com/v1.0/me/mailFolders?$select=totalItemCount', headers=headers)
personal_mails_data = pd.json_normalize(request.json(), record_path=['value'])
nbMail = str(personal_mails_data['totalItemCount'].sum()) + " mails"
print(nbMail)


# Can't work
# %%
request = requests.get("https://graph.microsoft.com/v1.0/users?$select=id", headers=headers)
ids = pd.json_normalize(request.json(), record_path=['value'])
print(ids)
TotalNbMail = 0
for i in range(len(ids.index)):
    id = ids.iloc[i]['id']
    print(id)
    request = requests.get(f"https://graph.microsoft.com/v1.0/users/{id}/mailFolders?$select=totalItemCount", headers=headers)
    print(request.content)
    mails_data = pd.json_normalize(request.json(), record_path=['value'])
    nbMail = mails_data['totalItemCount'].sum()
    print(nbMail)
    TotalNbMail += nbMail
print(TotalNbMail)


# %%
request = requests.get("https://graph.microsoft.com/v1.0/reports/getOffice365GroupsActivityDetail(period='D180')", headers=headers)
csv = request.content.decode("utf-8")
group_data = pd.read_csv(StringIO(csv), sep=",")
user_data = pd.DataFrame()
for i in range(len(group_data.index)):
    userPrincipalName = group_data['Owner Principal Name'][i]
    if isinstance(userPrincipalName, str):
        request = requests.get(f"https://graph.microsoft.com/v1.0/users/{userPrincipalName}?$select=userPrincipalName,displayName,jobTitle", headers=headers)
        user_data_tmp = pd.json_normalize(request.json())
        user_data = pd.concat([user_data, user_data_tmp])
group_data = pd.merge(group_data, user_data, left_on=["Owner Principal Name"], right_on=["userPrincipalName"], how="left")
display(group_data)
# %%
userPrincipalName = "mrenaux@itii-normandie.fr"
request = requests.get(f"https://graph.microsoft.com/v1.0/users/{userPrincipalName}", headers=headers)
user_data = pd.json_normalize(request.json())
request = requests.get("https://graph.microsoft.com/v1.0/reports/getOffice365GroupsActivityDetail(period='D180')", headers=headers)
csv = request.content.decode("utf-8")
group_data = pd.read_csv(StringIO(csv), sep=",")
group_data = pd.merge(group_data, user_data, left_on="Owner Principal Name", right_on="userPrincipalName", how="left")
display(group_data)
#%%
try:
    request = requests.get('https://graph.microsoft.com/v1.0/me/mailFolders?$select=totalItemCount', headers=headers)
    personal_mails_data = pd.json_normalize(request.json(), record_path=['value'])
    nbMail = personal_mails_data['totalItemCount'].sum()
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    data = [{'Last Update': date, 'nbMail':nbMail}]
    df = pd.DataFrame(data)
    df.to_pickle('static/assets/data/nbMail.pkl')
except:
    print("Data unreachable")

# %%
group_path = "static/assets/data/groupTable.pkl"
group_data = pd.read_pickle(group_path)
# group_data = group_data.groupby("Last Activity Date").size().reset_index(name='counts')
# group_data.to_pickle('static/assets/data/groupGraph.pkl')
# %%
request = requests.get(f"https://graph.microsoft.com/v1.0/users/?$select=userPrincipalName,displayName,jobTitle", headers=headers)
user_data = pd.json_normalize(request.json(), record_path=['value'])
nextLink = pd.json_normalize(request.json())['@odata.nextLink'][0]
while '@odata.nextLink' in pd.json_normalize(request.json()):
    request = requests.get(nextLink, headers=headers)
    user_data_tmp = pd.json_normalize(request.json(), record_path=['value'])
    if '@odata.nextLink' in pd.json_normalize(request.json()):
        nextLink = pd.json_normalize(request.json())['@odata.nextLink'][0]
    else:
        nextLink = False
    user_data = pd.concat([user_data, user_data_tmp])
    
request = requests.get(f"https://graph.microsoft.com/v1.0/groups?$select=id,deletedDateTime,createdDateTime", headers=headers)
group_data = pd.json_normalize(request.json(), record_path=['value'])
nextLink = pd.json_normalize(request.json())['@odata.nextLink'][0]
while '@odata.nextLink' in pd.json_normalize(request.json()):
    request = requests.get(nextLink, headers=headers)
    group_data_tmp = pd.json_normalize(request.json(), record_path=['value'])
    if '@odata.nextLink' in pd.json_normalize(request.json()):
        nextLink = pd.json_normalize(request.json())['@odata.nextLink'][0]
    else:
        nextLink = False
    group_data = pd.concat([group_data, group_data_tmp])
group_data['createdDateTime'] = pd.to_datetime(group_data['createdDateTime']).dt.strftime("%Y-%m-%d")
group_data['deletedDateTime'] = pd.to_datetime(group_data['deletedDateTime']).dt.strftime("%Y-%m-%d")

request = requests.get("https://graph.microsoft.com/v1.0/reports/getOffice365GroupsActivityDetail(period='D180')", headers=headers)
if request.status_code != 401:
    csv = request.content.decode("utf-8")
    groups_data = pd.read_csv(StringIO(csv), sep=",")
    groups_data = pd.merge(groups_data, user_data, left_on=["Owner Principal Name"], right_on=["userPrincipalName"], how="left")
    groups_data = pd.merge(groups_data, group_data, left_on=["Group Id"], right_on=["id"], how="left")
    # Remove NaN :
    groups_data.fillna('None')
groups_data.to_pickle('static/assets/data/groupTable.pkl')


# %%
request = requests.get("https://graph.microsoft.com/v1.0/reports/getOffice365GroupsActivityDetail(period='D180')", headers=headers)
if request.status_code != 401:
    csv = request.content.decode("utf-8")
    group_data = pd.read_csv(StringIO(csv), sep=",")
    request = requests.get(f"https://graph.microsoft.com/v1.0/users/?$select=userPrincipalName,displayName,jobTitle", headers=headers)
    user_data = pd.json_normalize(request.json(), record_path=['value'])
    group_data = pd.merge(group_data, user_data, left_on=["Owner Principal Name"], right_on=["userPrincipalName"], how="left")
    # Remove NaN :
    group_data[['displayName', 'jobTitle', 'Owner Principal Name', 'Last Activity Date']] = group_data[['displayName', 'jobTitle', 'Owner Principal Name', 'Last Activity Date']].fillna('None')
    #group_data["Exchange Mailbox Storage Used (Byte)"] = group_data["Exchange Mailbox Storage Used (Byte)"]/(1024e4)
    #group_data.to_pickle('static/assets/data/groupTable.pkl')
# %%
group_path = "static/assets/data/groupTable.pkl"
group_data = pd.read_pickle(group_path)
group_graph = group_data[group_data['Is Deleted'] == False].groupby("Last Activity Date").size().reset_index(name='counts')
group_graph.to_pickle('static/assets/data/ActiveGroupGraphDay.pkl')
group_graph = group_data[group_data['Is Deleted'] == True].groupby("Last Activity Date").size().reset_index(name='counts')
group_graph.to_pickle('static/assets/data/DeletedGroupGraphDay.pkl')

group_data['Last Activity Date'] = pd.to_datetime(group_data['Last Activity Date'])
group_graph = group_data[group_data['Is Deleted'] == False].groupby(group_data['Last Activity Date'].dt.to_period('M')).size().reset_index(name='counts')
group_graph.to_pickle('static/assets/data/ActiveGroupGraphMonth.pkl')
group_graph = group_data[group_data['Is Deleted'] == True].groupby(group_data['Last Activity Date'].dt.to_period('M')).size().reset_index(name='counts')
group_graph.to_pickle('static/assets/data/DeletedGroupGraphMonth.pkl')

# %%
group_path = "static/assets/data/groupTable.pkl"
group_data = pd.read_pickle(group_path)

# group_info = pd.DataFrame()
# group_info.at[0, 'Deleted'] = group_data[group_data['Is Deleted'] == True].count()['Is Deleted']
# group_info.at[0, 'Active'] = group_data[group_data['Is Deleted'] == False].count()['Is Deleted']
# group_info.to_pickle('static/assets/data/GroupInfo.pkl')
# %%
user_path = "static/assets/data/licenseTable.pkl"
user_data = pd.read_pickle(user_path)
# user_data = user_data.fillna('Vide')
# user_data.to_pickle('static/assets/data/userTable.pkl')
# %%
license_data = pd.read_csv("static/assets/data/licenseID2ProductName.csv",encoding='cp1252')
license_data.to_pickle('static/assets/data/licenseID2ProductName.pkl')
# %%
licenseID2ProductName_path = "static/assets/data/licenseID2ProductName.pkl"
licenseID2ProductName_data = pd.read_pickle(licenseID2ProductName_path)
request = requests.get(f"https://graph.microsoft.com/v1.0/subscribedSkus", headers=headers)
if request.status_code != 401:
    licenses_data = pd.json_normalize(request.json(), record_path=['value'])
    licenses_data = pd.merge(licenses_data, licenseID2ProductName_data, left_on=["skuPartNumber"], right_on=["String_Id"], how="left").drop_duplicates(subset=['Product_Display_Name'])
    licenses_data = licenses_data.fillna('Vide')
    licenses_data.to_pickle('static/assets/data/licenseTable.pkl')
# %%
request = requests.get(f"https://graph.microsoft.com/v1.0/groups?$expand=owners", headers=headers)
if request.status_code != 401:
    group_data = pd.json_normalize(request.json(), record_path=['value'])
    nextLink = pd.json_normalize(request.json())['@odata.nextLink'][0]
    while '@odata.nextLink' in pd.json_normalize(request.json()):
        request = requests.get(nextLink, headers=headers)
        group_data_tmp = pd.json_normalize(request.json(), record_path=['value'])
        if '@odata.nextLink' in pd.json_normalize(request.json()):
            nextLink = pd.json_normalize(request.json())['@odata.nextLink'][0]
        else:
            nextLink = False
        group_data = pd.concat([group_data, group_data_tmp])
    group_data['createdDateTime'] = pd.to_datetime(group_data['createdDateTime']).dt.strftime("%Y-%m-%d")
    group_data['deletedDateTime'] = pd.to_datetime(group_data['deletedDateTime']).dt.strftime("%Y-%m-%d")
    
#%%
def nextLink(url, record_path=None, meta=None):
    df_data = pd.DataFrame() 
    while url:
        request = requests.get(url, headers=headers).json()
        df_data_tmp = pd.json_normalize(request, record_path=record_path, meta=meta)
        df_data = pd.concat([df_data, df_data_tmp]) 
        if '@odata.nextLink' in request:
            url = request['@odata.nextLink']
        else:
            url = None        
    return df_data.reset_index(drop=True)

# active_groups_data = pd.concat([
#                                 nextLink("https://graph.microsoft.com/v1.0/groups?$expand=owners($select=userPrincipalName)&$select=id,displayName,createdDateTime,resourceProvisioningOptions,renewedDateTime,deletedDateTime", ['value']),
#                                 nextLink("https://graph.microsoft.com/v1.0/groups?$expand=members($select=userPrincipalName)&$select=id", ['value'])
#                                 ])
df_active_groups_data = nextLink("https://graph.microsoft.com/v1.0/groups?$expand=owners($select=userPrincipalName)&$select=id,displayName,createdDateTime,resourceProvisioningOptions,renewedDateTime", ['value'])
df_active_groups_members = nextLink("https://graph.microsoft.com/v1.0/groups?$expand=members($select=userPrincipalName)&$select=id", ['value'])
df_deleted_groups_data = nextLink("https://graph.microsoft.com/v1.0/directory/deletedItems/microsoft.graph.group", ['value'])

def flattenColumn(column):
    user_principal_names = []
    for obj_list in column:
        user_principal_names.append([obj['userPrincipalName'] for obj in obj_list if 'userPrincipalName' in obj])
    return user_principal_names

df_active_groups_data['members.userPrincipalNames'] = flattenColumn(df_active_groups_members['members'])
df_active_groups_data['owners.userPrincipalNames'] = flattenColumn(df_active_groups_data['owners'])
df_active_groups_data.drop(columns=['owners'])

# request = requests.get("https://graph.microsoft.com/v1.0/reports/getOffice365GroupsActivityDetail(period='D180')", headers=headers)
# if request.status_code != 401:
#     csv = request.content.decode("utf-8")
#     group_data = pd.read_csv(StringIO(csv), sep=",")
#     group_data = pd.merge(group_data, user_data, left_on=["Owner Principal Name"], right_on=["userPrincipalName"], how="left")

# df_active_groups_data.to_pickle('static/assets/data/df_active_groups_data.pkl')
# df_deleted_groups_data.to_pickle('static/assets/data/df_deleted_groups_data.pkl')

# %%
df_test = pd.read_pickle('static/assets/data/df_active_groups_data.pkl')
df_active_groups_data = pd.json_normalize(df_test['value'][0])

def flattenColumn(column):
    user_principal_names = []
    for obj_list in column:
        user_principal_names.append([obj['userPrincipalName'] for obj in obj_list if 'userPrincipalName' in obj])
    return user_principal_names

df_active_groups_data['owners.userPrincipalNames'] = flattenColumn(df_active_groups_data['owners'])
df_active_groups_data.drop(columns=['owners'])

# %%
group_path = "static/assets/data/groupTable.pkl"
group_data = pd.read_pickle(group_path)

id = 0
for obj in group_data['owners.userPrincipalNames']:
    for owner in obj:
        print(owner, id)
    id += 1
# %%
def flattenColumn(column):
    user_principal_names = []
    for obj_list in column:
        user_principal_names.append([obj['userPrincipalName'] for obj in obj_list if 'userPrincipalName' in obj])
    return user_principal_names
def nextLink(url, record_path=None, meta=None):
    df_data = pd.DataFrame() 
    while url:
        request = requests.get(url, headers=headers).json()
        df_data_tmp = pd.json_normalize(request, record_path=record_path, meta=meta)
        df_data = pd.concat([df_data, df_data_tmp]) 
        if '@odata.nextLink' in request:
            url = request['@odata.nextLink']
        else:
            url = None        
    return df_data.reset_index(drop=True)
user_path = "static/assets/data/userTable.pkl"
user_data = pd.read_pickle(user_path)
    
group_data = nextLink(f"https://graph.microsoft.com/v1.0/groups?$expand=owners", record_path=['value'])
group_data['createdDateTime'] = pd.to_datetime(group_data['createdDateTime']).dt.strftime("%Y-%m-%d")
group_data['owners.userPrincipalNames'] = flattenColumn(group_data['owners'])
group_data.drop(columns=['owners'])

df_deleted_groups_data = nextLink("https://graph.microsoft.com/v1.0/directory/deletedItems/microsoft.graph.group", ['value'])


request = requests.get("https://graph.microsoft.com/v1.0/reports/getOffice365GroupsActivityDetail(period='D30')", headers=headers)
csv = request.content.decode("utf-8")
reports_groups_data = pd.read_csv(StringIO(csv), sep=",")
reports_groups_data = pd.merge(reports_groups_data, user_data, left_on=["Owner Principal Name"], right_on=["userPrincipalName"], how="left")
reports_groups_data = pd.merge(reports_groups_data, group_data, left_on=["Group Id"], right_on=["id"], how="left")
# Remove NaN :
reports_groups_data = reports_groups_data.fillna('Vide')
reports_groups_data.to_pickle('static/assets/data/groupTable.pkl')
# %%
df = pd.read_pickle('static/assets/data/groupTable.pkl')




# %%
def flattenColumn(column):
    user_principal_names = []
    for obj_list in column:
        user_principal_names.append([obj['userPrincipalName'] for obj in obj_list if 'userPrincipalName' in obj])
    return user_principal_names
def nextLink(url, record_path=None, meta=None):
    df_data = pd.DataFrame() 
    while url:
        request = requests.get(url, headers=headers).json()
        df_data_tmp = pd.json_normalize(request, record_path=record_path, meta=meta)
        df_data = pd.concat([df_data, df_data_tmp]) 
        if '@odata.nextLink' in request:
            url = request['@odata.nextLink']
        else:
            url = None        
    return df_data.reset_index(drop=True)

user_path = "static/assets/data/userTable.pkl"
user_data = pd.read_pickle(user_path)
    
group_data = nextLink(f"https://graph.microsoft.com/v1.0/groups?$expand=owners", record_path=['value'])
group_data['createdDateTime'] = pd.to_datetime(group_data['createdDateTime']).dt.strftime("%Y-%m-%d")
group_data['owners.userPrincipalNames'] = flattenColumn(group_data['owners'])
group_data = group_data[["id","resourceProvisioningOptions","createdDateTime","owners.userPrincipalNames"]]
group_data.rename(columns={'id':'Group Id'}, inplace=True)

df_deleted_groups_data = nextLink("https://graph.microsoft.com/v1.0/directory/deletedItems/microsoft.graph.group", ['value'])
df_deleted_groups_data = df_deleted_groups_data[["deletedDateTime","id"]]
df_deleted_groups_data.rename(columns={'id':'Group Id'}, inplace=True)

request = requests.get("https://graph.microsoft.com/v1.0/reports/getOffice365GroupsActivityDetail(period='D30')", headers=headers)
csv = request.content.decode("utf-8")

reports_groups_data = pd.read_csv(StringIO(csv), sep=",")
reports_groups_data = reports_groups_data[["Group Id","Group Display Name","Owner Principal Name","Is Deleted","Last Activity Date","Member Count","Report Refresh Date"]]

reports_groups_data = pd.merge(reports_groups_data, user_data, left_on=["Owner Principal Name"], right_on=["userPrincipalName"], how="left")
reports_groups_data = pd.merge(reports_groups_data, group_data, left_on=["Group Id"], right_on=["Group Id"], how="left")

reports_groups_data = pd.merge(reports_groups_data, df_deleted_groups_data, left_on=["Group Id"], right_on=["Group Id"], how='left')
reports_groups_data["Is Deleted"][reports_groups_data.index[reports_groups_data["deletedDateTime"].notnull()]] = True
# Remove NaN :
reports_groups_data = reports_groups_data.fillna('Vide')




# %%
df = pd.read_excel('static/assets/data/Compteur.xlsx')
# %%
request = requests.get("https://graph.microsoft.com/v1.0/reports/getMailboxUsageDetail(period='D30')", headers=headers)
csv = request.content.decode("utf-8")
reports_mails_data = pd.read_csv(StringIO(csv), sep=",")
reports_mails_data = reports_mails_data[["User Principal Name","Display Name","Report Refresh Date","Item Count","Storage Used (Byte)"]]
reports_mails_data["Converted Storage"] = reports_mails_data["Storage Used (Byte)"].apply(size)
reports_mails_data.to_pickle('static/assets/data/MailsTable.pkl')

# %%
df = pd.read_pickle('static/assets/data/MailsTable.pkl')
# %%
def nextLink(url, record_path=None, meta=None):
    df_data = pd.DataFrame() 
    while url:
        request = requests.get(url, headers=headers).json()
        df_data_tmp = pd.json_normalize(request, record_path=record_path, meta=meta)
        df_data = pd.concat([df_data, df_data_tmp]) 
        if '@odata.nextLink' in request:
            url = request['@odata.nextLink']
        else:
            url = None        
    return df_data.reset_index(drop=True)

user_data = nextLink("https://graph.microsoft.com/v1.0/users/?$select=userPrincipalName,DisplayName,jobTitle,department,accountEnabled,createdDateTime", ['value'])
user_data = user_data.fillna('Vide')
user_data.to_pickle('static/assets/data/userTable.pkl')
# %%

user_path = "static/assets/data/userTable.pkl"
user_data = pd.read_pickle(user_path)

mails_path = "static/assets/data/MailsTable.pkl"
mails_data = pd.read_pickle(mails_path)
  
  
data = user_data.merge(mails_data, left_on="userPrincipalName", right_on="User Principal Name")


#%%
absences_path = "static/assets/data/absences.xlsx"
absences_data = pd.read_excel(absences_path)

absences_data[['dateFin', 'dateDebut']] = absences_data[['dateFin', 'dateDebut']].apply(pd.to_datetime)
absences_data['Duration'] = (absences_data['dateFin'] - absences_data['dateDebut']).dt.days

firstDate = pd.to_datetime(datetime.date(2023, 1, 1))
endDate = pd.to_datetime(datetime.date(2023, 12, 1))


for trg in absences_data["trg"].drop_duplicates():

    trg_absences_data = absences_data[absences_data["trg"].str.contains(trg)].reset_index(drop=True)
    trg_absences_data = trg_absences_data.sort_values(by=["dateDebut"], ascending=True).reset_index(drop=True)

    datasets = [ [] for _ in range(len(trg_absences_data)) ]
    for index in range(len(trg_absences_data)):
        if index == 0:
            date = firstDate
            var = (trg_absences_data['dateDebut'][index] - date).days
            dataset = [
                        var,
                        var + trg_absences_data['Duration'][index]
                        ]
        else:
            date = trg_absences_data['dateFin'][index - 1]
            var = (trg_absences_data['dateDebut'][index] - date).days
            previous_dataset = datasets[index - 1][0]
            dataset = [
                        previous_dataset[1] + var,
                        previous_dataset[1] + var + trg_absences_data['Duration'][index]
                        ]
        datasets[index].append(dataset)

    print(datasets)



    

absences_data = absences_data[absences_data["trg"].str.contains("MFL")].reset_index(drop=True)
absences_data = absences_data.sort_values(by=["dateDebut"], ascending=True).reset_index(drop=True)

datasets = [ [] for _ in range(len(absences_data)) ]
for index in range(len(absences_data)):
    if index == 0:
        date = firstDate
        var = (absences_data['dateDebut'][index] - date).days
        dataset = [
                    var,
                    var + absences_data['Duration'][index]
                    ]
    else:
        date = absences_data['dateFin'][index - 1]
        var = (absences_data['dateDebut'][index] - date).days
        previous_dataset = datasets[index - 1][0]
        dataset = [
                    previous_dataset[1] + var,
                    previous_dataset[1] + var + absences_data['Duration'][index]
                    ]
    datasets[index].append(dataset)

        
        
    # dataset1 = [[
    #             var,
    #             var + absences_data['Duration'][index]
    #             ]]
    # dataset2 = [[
    #             dataset1[index][0] + var,
    #             dataset1[index][0] + var + absences_data['Duration'][index]
    #             ]]



# ds1_var = (absences_data['dateDebut'][0] - firstDate).days
# ds1 = [[
#         ds1_var,
#         (ds1_var + absences_data['Duration'][0])
#         ]]

# ds2_var = (absences_data['dateDebut'][1] - absences_data['dateFin'][0]).days
# ds2 = [[
#         ds1[trg_index][1] + ds2_var, 
#         ds1[trg_index][1] + absences_data['Duration'][1] + ds2_var
#         ]]

# ds3_var = (absences_data['dateDebut'][2] - absences_data['dateFin'][1]).days
# ds3 = [[
#         ds2[trg_index][1] + ds3_var, 
#         ds2[trg_index][1] + absences_data['Duration'][2] + ds3_var
#         ]]



# %%
absences_path = "static/assets/data/absences.xlsx"
absences_data = pd.read_excel(absences_path)

absences_data[['dateFin', 'dateDebut']] = absences_data[['dateFin', 'dateDebut']].apply(pd.to_datetime)
absences_data['Duration'] = (absences_data['dateFin'] - absences_data['dateDebut']).dt.days

firstDate = pd.to_datetime(datetime.date(2023, 1, 1))
endDate = pd.to_datetime(datetime.date(2023, 12, 1))


datasets_final = [ [] for _ in range(len(trg_absences_data)) ]
for trg in absences_data["trg"].drop_duplicates():

    trg_absences_data = absences_data[absences_data["trg"].str.contains(trg)].reset_index(drop=True)
    trg_absences_data = trg_absences_data.sort_values(by=["dateDebut"], ascending=True).reset_index(drop=True)

    datasets = [ [] for _ in range(len(trg_absences_data)) ]
    for index in range(len(trg_absences_data)):
        if index == 0:
            date = firstDate
            var = (trg_absences_data['dateDebut'][index] - date).days
            dataset = [
                        var,
                        var + trg_absences_data['Duration'][index]
                        ]
        else:
            date = trg_absences_data['dateFin'][index - 1]
            var = (trg_absences_data['dateDebut'][index] - date).days
            previous_dataset = datasets[index - 1][0]
            dataset = [
                        previous_dataset[1] + var,
                        previous_dataset[1] + var + trg_absences_data['Duration'][index]
                        ]
        datasets[index].append(dataset)

    print(datasets)
    
    
# %%
absences_path = "static/assets/data/absences.xlsx"
absences_data = pd.read_excel(absences_path)

absences_data[['dateFin', 'dateDebut']] = absences_data[['dateFin', 'dateDebut']].apply(pd.to_datetime)
absences_data['Duration'] = (absences_data['dateFin'] - absences_data['dateDebut']).dt.days

firstDate = pd.to_datetime(datetime.date(2023, 1, 1))
endDate = pd.to_datetime(datetime.date(2023, 12, 1))

datasets_final = [ [ [] for _ in range(5) ] for _ in range(100) ]
for idx, trg in enumerate(absences_data["trg"].drop_duplicates()):

    trg_absences_data = absences_data[absences_data["trg"].str.contains(trg)].reset_index(drop=True)
    trg_absences_data = trg_absences_data.sort_values(by=["dateDebut"], ascending=True).reset_index(drop=True)

    datasets = [ [] for _ in range(len(trg_absences_data)) ]
    for index in range(len(trg_absences_data)):
        if index == 0:
            date = firstDate
            var = (trg_absences_data['dateDebut'][index] - date).days
            dataset = [
                        var,
                        var + trg_absences_data['Duration'][index]
                        ]
        else:
            date = trg_absences_data['dateFin'][index - 1]
            var = (trg_absences_data['dateDebut'][index] - date).days
            previous_dataset = datasets[index - 1][0]
            dataset = [
                        previous_dataset[1] + var,
                        previous_dataset[1] + var + trg_absences_data['Duration'][index]
                        ]
        datasets[index].append(dataset)
        print(dataset, index, trg)
        datasets_final[index][idx] = dataset

print(datasets_final)



# %%
absences_path = "static/assets/data/absences.xlsx"
absences_data = pd.read_excel(absences_path)

absences_data[['dateFin', 'dateDebut']] = absences_data[['dateFin', 'dateDebut']].apply(pd.to_datetime)
absences_data['Duration'] = (absences_data['dateFin'] - absences_data['dateDebut']).dt.days

firstDate = pd.to_datetime(datetime.date(2023, 1, 1))
endDate = pd.to_datetime(datetime.date(2023, 12, 1))

trg_data = ["MFL","IEL","PEL","LCL","KLE"]
dataset_final = [ [ [] for _ in range(len(trg_data)) ] for _ in range(absences_data.pivot_table(index = ['trg'], aggfunc ='size').max()) ]
for idx, trg in enumerate(trg_data):

    trg_absences_data = absences_data[absences_data["trg"].str.contains(trg)].reset_index(drop=True)
    trg_absences_data = trg_absences_data.sort_values(by=["dateDebut"], ascending=True).reset_index(drop=True)

    datasets = [ [] for _ in range(len(trg_absences_data)) ]
    for index in range(len(trg_absences_data)):
        if index == 0:
            date = firstDate
            var = (trg_absences_data['dateDebut'][index] - date).days
            dataset = [
                        var,
                        var + trg_absences_data['Duration'][index]
                        ]
        else:
            date = trg_absences_data['dateFin'][index - 1]
            var = (trg_absences_data['dateDebut'][index] - date).days
            previous_dataset = datasets[index - 1][0]
            dataset = [
                        previous_dataset[1] + var,
                        previous_dataset[1] + var + trg_absences_data['Duration'][index]
                        ]
        datasets[index].append(dataset)
        print(dataset, index, trg, idx)
        dataset_final[index][idx] = dataset

print(dataset_final)
        

# %%
dataset_final = []
if not absences_data.empty:
    date_today = pd.to_datetime(datetime.datetime.now().date())
    absences_data[['dateFin', 'dateDebut']] = absences_data[['dateFin', 'dateDebut']].apply(pd.to_datetime, dayfirst=True)

    absences_data['Is Past'] = False
    absences_data['Is Past'][absences_data.index[absences_data['dateFin'] < date_today]] = True

    absences_data['dateFin'] = absences_data['dateFin'] + datetime.timedelta(days=1)

    absences_data['In Progress'] = False
    absences_data['In Progress'][(absences_data['dateDebut'] <= date_today) & (absences_data['dateFin'] >= date_today)] = True

    absences_data['Starts In'] = ((absences_data['dateDebut'][absences_data['Is Past'] == False] - date_today).dt.days)
    absences_data['Starts In'] = absences_data['Starts In'].fillna(0).astype(int)
    absences_data['Ends In'] = (absences_data['dateFin'][absences_data['Is Past'] == False] - date_today).dt.days
    absences_data['Ends In'] = absences_data['Ends In'].fillna(0).astype(int)

    absences_data['dateFin'] = absences_data['dateFin'] - datetime.timedelta(days=1)

    absences_data['Duration'] = (absences_data['dateFin'] - absences_data['dateDebut']).dt.days

    firstDate = pd.to_datetime(datetime.date(2023, 1, 1), dayfirst=True)


    trg_data = ["MFL","IEL","PEL","LCL","KLE"]
    dataset_final = [ [ [] for _ in range(len(trg_data)) ] for _ in range(absences_data.pivot_table(index = ['trg'], aggfunc ='size').max()) ]
    for idx, trg in enumerate(trg_data):

        trg_absences_data = absences_data[absences_data["trg"].str.contains(trg)].reset_index(drop=True)
        trg_absences_data = trg_absences_data.sort_values(by=["dateDebut"], ascending=True).reset_index(drop=True)

        datasets = [ [] for _ in range(len(trg_absences_data)) ]
        for index in range(len(trg_absences_data)):
            if index == 0:
                date = firstDate
                var = (trg_absences_data['dateDebut'][index] - date).days
                dataset = [
                            var,
                            var + trg_absences_data['Duration'][index] + 1
                            ]
            else:
                date = trg_absences_data['dateFin'][index - 1]
                var = (trg_absences_data['dateDebut'][index] - date).days
                previous_dataset = datasets[index - 1][0]
                dataset = [
                            previous_dataset[1] + var,
                            previous_dataset[1] + var + trg_absences_data['Duration'][index] + 1
                            ]
            datasets[index].append(dataset)
            dataset_final[index][idx] = dataset
            
    for i in range(len(dataset_final)):
        for j in range(len(dataset_final[i])):
            if dataset_final[i][j] == []:
                dataset_final[i][j] = [-1,-1]
                
                
#%%
absences_path = "static/assets/data/absences.xlsx"
absences_data = pd.read_excel(absences_path)

dataset_final = []
if not absences_data.empty:
    absences_data[['dateFin', 'dateDebut']] = absences_data[['dateFin', 'dateDebut']].apply(pd.to_datetime, dayfirst=True)
    
    absences_data['Duration'] = (absences_data['dateFin'] - absences_data['dateDebut']).dt.days

    firstDate = pd.to_datetime(datetime.date(2023, 1, 1), dayfirst=True)

    trg_data = ["MFL", "IEL", "PEL", "LCL", "KLE"]
    max_size = absences_data.pivot_table(index='trg', aggfunc='size').max()
    dataset_final = [[[-1, -1] for _ in range(len(trg_data))] for _ in range(max_size)]

    for idx, trg in enumerate(trg_data):
        trg_absences_data = absences_data[absences_data["trg"].str.contains(trg)].reset_index(drop=True)
        trg_absences_data = trg_absences_data.sort_values(by="dateDebut").reset_index(drop=True)

        datasets = [[] for _ in range(len(trg_absences_data))]
        for index in range(len(trg_absences_data)):
            if index == 0:
                date = firstDate
            else:
                date = trg_absences_data['dateFin'][index - 1]

            var = (trg_absences_data['dateDebut'][index] - date).days
            previous_dataset = datasets[index - 1][0] if index > 0 else [-1, -1]
            dataset = [
                previous_dataset[1] + var,
                previous_dataset[1] + var + trg_absences_data['Duration'][index] + 1
            ]
            datasets[index].append(dataset)
            dataset_final[index][idx] = dataset

    print(dataset_final)
    df = pd.DataFrame(dataset_final)
    df.to_pickle('static/assets/data/datasetsGraphAbsences.pkl')
# %%
user_path = "static/assets/data/userTable.pkl"
user_data = pd.read_pickle(user_path)
userLastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(user_path)).strftime("%d/%m/%Y %H:%M:%S")

mails_path = "static/assets/data/MailsTable.pkl"
mails_data = pd.read_pickle(mails_path)

group_path = "static/assets/data/groupTable.pkl"
group_data = pd.read_pickle(group_path)
groupLastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(group_path)).strftime("%d/%m/%Y %H:%M:%S")

compteur_path = "static/assets/data/Compteur.xlsx"
df_compteur_data = pd.read_excel(compteur_path)

absences_path = "static/assets/data/absences.xlsx"
absences_data = pd.read_excel(absences_path)

datasetsGraphAbsences_path = "static/assets/data/datasetsGraphAbsences.pkl"
dataset_final = pd.read_pickle(datasetsGraphAbsences_path)

mailsSI_data = mails_data.loc[mails_data["Display Name"].str.contains('Magali FLAVIGNY') | 
                            mails_data["Display Name"].str.contains('Ilyas ELAMRI') |
                            mails_data["Display Name"].str.contains('Pierre-Emmanuel LECONTE') |
                            mails_data["Display Name"].str.contains('Laurent CLAY') |
                            mails_data["Display Name"].str.contains('Kevin LECHÊNE')].reset_index(drop=True)

compteurlastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(compteur_path)).strftime("%d/%m/%Y %H:%M:%S")
absenceslastUpdate = datetime.datetime.fromtimestamp(os.path.getmtime(absences_path)).strftime("%d/%m/%Y %H:%M:%S")
mailslastUpdate = mailsSI_data['Report Refresh Date'][0]

if not absences_data.empty:
    date_today = pd.to_datetime(datetime.datetime.now().date())
    absences_data[['dateFin', 'dateDebut']] = absences_data[['dateFin', 'dateDebut']].apply(pd.to_datetime, dayfirst=True)

    absences_data['Is Past'] = absences_data['dateFin'] < date_today
    absences_data = absences_data[absences_data['Is Past'] == False ]

    absences_data['dateFin'] += pd.Timedelta(days=1)

    absences_data['In Progress'] = (absences_data['dateDebut'] <= date_today) & (absences_data['dateFin'] >= date_today)

    absences_data['Starts In'] = (absences_data['dateDebut'][~absences_data['Is Past']] - date_today).dt.days
    absences_data['Starts In'] = absences_data['Starts In'].fillna(0).astype(int)
    absences_data['Ends In'] = (absences_data['dateFin'][~absences_data['Is Past']] - date_today).dt.days
    absences_data['Ends In'] = absences_data['Ends In'].fillna(0).astype(int)

    absences_data['dateFin'] -= pd.Timedelta(days=1)
# %%
user_path = "static/assets/data/groupTable.pkl"
user_data = pd.read_pickle(user_path)
# %%



def nextLink(url, record_path=None, meta=None):
    df_data = pd.DataFrame() 
    while url:
        request = requests.get(url, headers=headers).json()
        df_data_tmp = pd.json_normalize(request, record_path=record_path, meta=meta)
        df_data = pd.concat([df_data, df_data_tmp]) 
        if '@odata.nextLink' in request:
            url = request['@odata.nextLink']
        else:
            url = None
    return df_data.reset_index(drop=True)
def flattenColumn(column):
    user_principal_names = []
    for obj_list in column:
        user_principal_names.append([obj['userPrincipalName'] for obj in obj_list if 'userPrincipalName' in obj])
    return user_principal_names

user_path = "static/assets/data/userTable.pkl"
user_data = pd.read_pickle(user_path)
user_data = user_data[["userPrincipalName","displayName","jobTitle","department","accountEnabled"]]

group_data = nextLink(f"https://graph.microsoft.com/v1.0/groups?$expand=owners", record_path=['value'])
# group_data['createdDateTime'] = pd.to_datetime(group_data['createdDateTime']).dt.strftime("%Y-%m-%d")
group_data['owners.userPrincipalNames'] = flattenColumn(group_data['owners'])
group_data = group_data[["id","resourceProvisioningOptions","createdDateTime","owners.userPrincipalNames"]]
group_data.rename(columns={'id':'Group Id'}, inplace=True)

df_deleted_groups_data = nextLink("https://graph.microsoft.com/v1.0/directory/deletedItems/microsoft.graph.group", ['value'])
df_deleted_groups_data = df_deleted_groups_data[["deletedDateTime","id"]]
df_deleted_groups_data.rename(columns={'id':'Group Id'}, inplace=True)

request = requests.get("https://graph.microsoft.com/v1.0/reports/getOffice365GroupsActivityDetail(period='D30')", headers=headers)
csv = request.content.decode("utf-8")

reports_groups_data = pd.read_csv(StringIO(csv), sep=",")
reports_groups_data = reports_groups_data[["Group Id","Group Display Name","Owner Principal Name","Is Deleted","Last Activity Date","Member Count","Report Refresh Date"]]

reports_groups_data = pd.merge(reports_groups_data, user_data, left_on=["Owner Principal Name"], right_on=["userPrincipalName"], how="left")
reports_groups_data = pd.merge(reports_groups_data, group_data, left_on=["Group Id"], right_on=["Group Id"], how="left")

reports_groups_data = pd.merge(reports_groups_data, df_deleted_groups_data, left_on=["Group Id"], right_on=["Group Id"], how='left')
reports_groups_data["Is Deleted"][reports_groups_data.index[reports_groups_data["deletedDateTime"].notnull()]] = True
# Remove NaN :
reports_groups_data = reports_groups_data.fillna('Vide')
reports_groups_data.to_pickle('static/assets/data/groupTable.pkl')







# %%
import itertools
def nextLink(url, record_path=None, meta=None):
    df_data = pd.DataFrame() 
    while url:
        request = requests.get(url, headers=headers).json()
        df_data_tmp = pd.json_normalize(request, record_path=record_path, meta=meta)
        df_data = pd.concat([df_data, df_data_tmp]) 
        if '@odata.nextLink' in request:
            url = request['@odata.nextLink']
        else:
            url = None
    return df_data.reset_index(drop=True)
def flattenColumn(column):
    user_principal_names = []
    for obj_list in column:
        user_principal_names.append([obj['userPrincipalName'] for obj in obj_list if 'userPrincipalName' in obj])
    return user_principal_names
user_data = nextLink("https://graph.microsoft.com/v1.0/users/?$select=id,userPrincipalName,mail,displayName,jobTitle,department,accountEnabled,companyName,userType,createdDateTime", ['value'])
user_data = user_data.fillna('Vide')
member_data = nextLink(f"https://graph.microsoft.com/v1.0/groups?$expand=members", record_path=['value'])
member_data['members_username'] = flattenColumn(member_data['members'])
member_data = member_data.explode('members_username')
member_data = member_data[['members_username']]
member_data = member_data.groupby('members_username').size().reset_index(name='size')
user_data = pd.merge(user_data, member_data, left_on=["userPrincipalName"], right_on=["members_username"], how="left")





# %%
request = requests.get("https://graph.microsoft.com/v1.0/reports/getOneDriveUsageAccountDetail(period='D30')", headers=headers)
csv = request.content.decode("utf-8")
onedrive_data = pd.read_csv(StringIO(csv), sep=",")
onedrive_data = onedrive_data[['Owner Display Name','File Count','Storage Used (Byte)']]
onedrive_data["Converted Storage"] = onedrive_data["Storage Used (Byte)"].apply(size)




# %%
df = pd.read_pickle("static/assets/data/groupTable.pkl")


# %%

user_path = "static/assets/data/userTable.pkl"
user_data = pd.read_pickle(user_path)

listTRG_data = []
listPhoto_data = []
for index in range(len(user_data)):
    id = user_data['id'][index]
    try:
        response = requests.get(f"https://graph.microsoft.com/beta/users/{id}/profile/names?$select=initials", headers=headers).json()
        trg = pd.json_normalize(response, record_path=['value'])
        listTRG_data.append(trg["initials"][0])
    except:
        listTRG_data.append("")

    try:
        photo_response = requests.get(f"https://graph.microsoft.com/v1.0/users/{id}/photo/$value", stream=True)
        photo = photo_response.raw.read()
        photo = base64.b64encode(photo).decode('utf-8')
        listPhoto_data.append(photo)
    except:   
        listPhoto_data.append("data:image/png;base64,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")
    
    
user_data["TRG"] = listTRG_data
user_data["Photo"] = listPhoto_data

user_data.to_pickle('static/assets/data/userTable.pkl')
# Approximately 12 minutes

#%%

user_path = "static/assets/data/userTable.pkl"
user_data = pd.read_pickle(user_path)

id = user_data['id'][1180]

photo_response = requests.get(f"https://graph.microsoft.com/v1.0/me/photo/$value", headers=headers)
image_content = photo_response.content
base64_image = base64.b64encode(image_content).decode('utf-8')
print(base64_image)


# %%
def nextLink(url, record_path=None, meta=None):
    df_data = pd.DataFrame() 
    while url:
        request = requests.get(url, headers=headers).json()
        df_data_tmp = pd.json_normalize(request, record_path=record_path, meta=meta)
        df_data = pd.concat([df_data, df_data_tmp]) 
        if '@odata.nextLink' in request:
            url = request['@odata.nextLink']
        else:
            url = None
    return df_data.reset_index(drop=True)
def flattenColumn(column):
    user_principal_names = []
    for obj_list in column:
        user_principal_names.append([obj['userPrincipalName'] for obj in obj_list if 'userPrincipalName' in obj])
    return user_principal_names

member_data = nextLink(f"https://graph.microsoft.com/v1.0/groups/a9727ee7-6e93-4f84-a583-ccdd8641d759/members/microsoft.graph.user", record_path=['value'])
member_data['members_username'] = flattenColumn(member_data['members'])
member_data = member_data.explode('members_username')
member_data = member_data[['members_username']]


# member_data = member_data.groupby('members_username').size().reset_index(name='size')



# %%

user_path = "static/assets/data/userTable.pkl"
user_data = pd.read_pickle(user_path)

list_data = []
for index in range(len(user_data)):
    id = user_data["id"][index]
    response = requests.get(f"https://graph.microsoft.com/v1.0/users/{id}/memberOf/$count", headers=headers).json()
    list_data.append(response)

user_data['Appartenances'] = list_data





# %%
user_path = "static/assets/data/userTable.pkl"
user_data = pd.read_pickle(user_path)

listPhone_data = []
for index in range(len(user_data)):
    id = user_data["id"][index]
    try:
        response = requests.get(f"https://graph.microsoft.com/beta/users/{id}/profile/phones?$select=type,number", headers=headers).json()
        phone = pd.json_normalize(response, record_path=['value'])
        number = phone[phone['type'].str.contains('home')]['number'][1]
        listPhone_data.append(number)
    except:
        listPhone_data.append("")
# %%
id ="34bbbacb-2639-467a-ab24-39b334011509"
request = nextLink("https://graph.microsoft.com/v1.0/groups/", record_path=['value'])
# %%
request = requests.get("https://graph.microsoft.com/v1.0/reports/getOffice365GroupsActivityDetail(period='D180')", headers=headers)
csv = request.content.decode("utf-8")

reports_groups_data = pd.read_csv(StringIO(csv), sep=",")
# %%
import base64
from io import StringIO
import json
import math
import os
from IPython.display import display
import pandas as pd
import requests
import datetime
import utils

mois = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Décembre']
annee = [2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
columns = ['mois','theme','date']

df = pd.DataFrame(columns=columns)
df['mois'] = mois
# display(df)

causeries_path = "static/assets/data/causeries.xlsx"
with pd.ExcelWriter(causeries_path) as writer:
    for i in range(len(annee)):
        print(annee[i])
        # if i == 0:
        #     df['theme'][0] = "Le bruit"
        # else : df['theme'][0] = ""
        df.to_excel(writer, sheet_name=str(annee[i]))

xls = pd.ExcelFile(causeries_path)

sheet_to_df_map = {}
for sheet_name in xls.sheet_names:
    sheet_to_df_map[sheet_name] = xls.parse(sheet_name, usecols=[1,2,3])
print(sheet_to_df_map)

sheet_index = 0
i = 0
date = "2023-06-07"

with pd.ExcelWriter(causeries_path) as writer:
    for index in range(len(sheet_to_df_map)):
        sheet = sheet_to_df_map[list(sheet_to_df_map)[index]]
        if index == sheet_index:
            sheet['date'][i] = date

        sheet.to_excel(writer, sheet_name=str(list(sheet_to_df_map)[index]))

#%%
mois = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Décembre']
annee = [2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
columns = ['annee','mois','theme','date']

df = pd.DataFrame(columns=columns)
# df['mois'] = mois
# df['annee'] = '2022/2023'


causeries_path = "static/assets/data/causeries.pkl"
df.to_pickle(causeries_path)


# %%

group_data = requests.get('https://raw.githubusercontent.com/microsoftgraph/dataconnect-solutions/main/sampledatasets/GroupDetails_v0.json').content.decode('utf-8')
print(type(group_data))
df = pd.read_json(group_data, lines=True)
df2 = df.explode('rowinformation').reset_index(drop=True)
display(df2)

# %%
