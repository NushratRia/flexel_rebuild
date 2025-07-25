from flask import Flask, request, render_template, redirect, url_for
import requests
import csv
import io
import re

app = Flask(__name__)

def get_sheet_name(sheet_id, gid):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid={gid}"
        response = requests.get(url)
        response.raise_for_status()
        html = response.text

        match = re.search(r'"gid":' + gid + r'.*?"title":"(.*?)"', html)
        if match:
            return match.group(1)
    except:
        pass
    return "Untitled Sheet"




@app.route('/view')
def view_sheet():
    csv_url = request.args.get('csv_url')
    sheet_name = request.args.get('sheet_name', 'Untitled Sheet')
    if not csv_url:
        return "Missing sheet URL."

    try:
        response = requests.get(csv_url)
        response.raise_for_status()
        f = io.StringIO(response.text)
        reader = list(csv.reader(f))
        headers = reader[0]
        data = reader[1:]
        return render_template('view.html', headers=headers, data=data, sheet_name=sheet_name)
    except Exception as e:
        return f"Failed to load sheet: {e}"





# @app.route('/view')
# def view_sheet():
#     csv_url = request.args.get('csv_url')
#     if not csv_url:
#         return "Missing sheet URL."

#     try:
#         response = requests.get(csv_url)
#         response.raise_for_status()
#         f = io.StringIO(response.text)
#         reader = list(csv.reader(f))
#         headers = reader[0]
#         data = reader[1:]
#         return render_template('view.html', headers=headers, data=data)
#     except Exception as e:
#         return f"Failed to load sheet: {e}"
    
    

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sheet_url = request.form['sheet_url']

        # Extract Sheet ID
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
        if not match:
            return "Invalid Google Sheets URL."
        sheet_id = match.group(1)

        # Extract gid (if present), otherwise default to 0
        gid_match = re.search(r'gid=([0-9]+)', sheet_url)
        gid = gid_match.group(1) if gid_match else '0'

        # Construct export link
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        sheet_name = get_sheet_name(sheet_id, gid)
        return redirect(url_for('view_sheet', csv_url=csv_url, sheet_name=sheet_name))


    return render_template('index.html')



    
    
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         sheet_url = request.form['sheet_url']

#         # Extract Sheet ID
#         match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
#         if not match:
#             return "Invalid Google Sheets URL."
#         sheet_id = match.group(1)

#         # Extract gid (if present), otherwise default to 0
#         gid_match = re.search(r'gid=([0-9]+)', sheet_url)
#         gid = gid_match.group(1) if gid_match else '0'

#         # Construct export link
#         csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
#         return redirect(url_for('view_sheet', csv_url=csv_url))

#     return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)

