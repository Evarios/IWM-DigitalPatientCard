from flask import Flask, render_template, redirect, url_for, request
from fhirpy import SyncFHIRClient

# setup
app = Flask(__name__)
client = SyncFHIRClient("http://localhost:8080/baseR4")


@app.route("/")
def home():
    return redirect(url_for("patients_page")) 


@app.route("/patientsList", methods=['POST', 'GET'])
def patients_page():
    if request.method == 'POST':
        surname = request.form['surname']
        resources = client.resources('Patient')
        patients = resources.search(name=[surname])
        patients_list = []
        for pt in patients:
            patient = {
                'name': pt['name'][0].given[0],
                'surname': pt['name'][0].family,
                'id': pt['id']
            }
            patients_list.append(patient)
        return render_template("patientsList.html", patients=patients_list)
    else:
        resources = client.resources('Patient')
        patients = resources.fetch_all()
        patients_list = []
        for pt in patients:
            patient = {
                'name': pt['name'][0].given[0],
                'surname': pt['name'][0].family,
                'id': pt['id']
            }
            patients_list.append(patient)
        return render_template("patientsList.html", patients=patients_list)


@app.route("/patient/<id>")
def patient_page(id):
    pt = client.reference('Patient', id).to_resource()
    patient = {
            'name': pt['name'][0].given[0],
            'surname': pt['name'][0].family,
            'id': pt['id']
    }
    return render_template("patientData.html", patient=patient)
    

if __name__ == "__main__":
    app.run(debug=True)
