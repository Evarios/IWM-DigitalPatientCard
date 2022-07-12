from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request
from fhirpy import SyncFHIRClient
from datetime import datetime
from dateutil import parser

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
    patient_reference = client.reference('Patient', id)
    patient_resource = patient_reference.to_resource()
    patient_birthdate_string =  patient_resource['birthDate']
    patient = {
            'name': patient_resource['name'][0].given[0],
            'surname': patient_resource['name'][0].family,
            'id': patient_resource['id'],
            'gender': patient_resource['gender'],
            'birthDate': parser.parse(patient_birthdate_string)
    }
    
    observations = client.resources('Observation').search(subject=patient_reference)
    observation_list = []
    for o in observations:
        observation = {}
        observation['name'] = o.to_resource()['code']['coding'][0]['display']
        observation_date_string = o.to_resource()['issued']
        observation['date'] = parser.parse(observation_date_string)
        if 'valueQuantity' in o:
            observation['value'] = o['valueQuantity']['value']
            observation['unit'] = o['valueQuantity']['unit']
        observation_list.append(observation)
    
    observation_list = sorted(observation_list, key= lambda d: d['date'], reverse=True)

    return render_template("patientData.html", patient_data=patient, medical_data=observation_list)
    

if __name__ == "__main__":
    patient = client.reference('Patient', '31191928-6acb-4d73-931c-e601cc3a13fa')
    observations = client.resources('Observation').search(subject=patient)
    print(patient.to_resource()['gender'])
    app.run(debug=True)
