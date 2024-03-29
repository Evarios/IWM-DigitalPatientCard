from flask import Flask, render_template, redirect, url_for, request
from fhirpy import SyncFHIRClient
from dateutil import parser
from datetime import datetime
import pytz

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


@app.route("/patient/<id>", methods=['POST', 'GET'])
def patient_page(id):
    if request.method == 'GET':
        patient_reference = client.reference('Patient', id)
        patient_resource = patient_reference.to_resource()
        patient_birthdate_string = patient_resource['birthDate']
        patient = {
            'name': patient_resource['name'][0].given[0],
            'surname': patient_resource['name'][0].family,
            'id': patient_resource['id'],
            'gender': patient_resource['gender'],
            'birthDate': parser.parse(patient_birthdate_string).strftime("%d/%m/%Y")
        }
        
        #Get observations
        observations = client.resources(
            'Observation').search(subject=patient_reference)
        observation_list = []
        for o in observations:
            observation = {}
            observation['typeString'] = "Obserwacja"
            observation['name'] = o.to_resource(
            )['code']['coding'][0]['display']
            observation_date_string = o.to_resource()['issued']
            observation['date'] = parser.parse(
                observation_date_string).strftime("%d/%m/%Y, %H:%M:%S")
            observation['dateSort'] = parser.parse(observation_date_string)
            if 'valueQuantity' in o:
                observation['value'] = round(o['valueQuantity']['value'], 2)
                observation['unit'] = o['valueQuantity']['unit']
            observation_list.append(observation)

        statements = client.resources(
            'MedicationRequest').search(subject=patient_reference)
        statements_list = []
        for s in statements:
            statement = {}
            statement['typeString'] = "Lekarstwo"
            statement['value'] = s['medicationCodeableConcept']['coding'][0]['display']
            statement_date_string = s['authoredOn']
            statement['date'] = parser.parse(statement_date_string).strftime("%d/%m/%Y, %H:%M:%S")
            statement['dateSort'] = parser.parse(statement_date_string)
            statements_list.append(statement)

        medical_data_list = observation_list + statements_list
        medical_data_list = sorted(medical_data_list, key=lambda d: d['dateSort'], reverse=True)

        return render_template("patientData.html", patient_data=patient, medical_data=medical_data_list)
    else:

        date_from = request.form['dateFrom']
        date_to = request.form['dateTo']

        datetime_from = datetime(1000, 1, 1)
        datetime_from.replace(tzinfo=pytz.utc)
        if date_from != "":
            datetime_from = parser.parse(date_from).replace(tzinfo=pytz.utc)

        datetime_to = datetime.now()
        datetime_to =  datetime_to.replace(tzinfo=pytz.utc)
        if date_to != "":
            datetime_to = parser.parse(date_to).replace(tzinfo=pytz.utc)

        patient_reference = client.reference('Patient', id)
        patient_resource = patient_reference.to_resource()
        patient_birthdate_string = patient_resource['birthDate']
        patient = {
            'name': patient_resource['name'][0].given[0],
            'surname': patient_resource['name'][0].family,
            'id': patient_resource['id'],
            'gender': patient_resource['gender'],
            'birthDate': parser.parse(patient_birthdate_string).strftime("%d/%m/%Y")
        }
        
        #get observations
        observations = client.resources(
            'Observation').search(subject=patient_reference)
        observation_list = []
        for o in observations:
            observation = {}
            observation['typeString'] = "Obserwacja"
            observation['name'] = o.to_resource(
            )['code']['coding'][0]['display']
            observation_date_string = o.to_resource()['issued']
            observation['date'] = parser.parse(
                observation_date_string).strftime("%d/%m/%Y, %H:%M:%S")
            observation['dateSort'] = parser.parse(observation_date_string).replace(tzinfo=pytz.utc)
            if 'valueQuantity' in o:
                observation['value'] = round(o['valueQuantity']['value'], 2)
                observation['unit'] = o['valueQuantity']['unit']
            if observation['dateSort'] <= datetime_to and date_from == "":
                observation_list.append(observation)
            elif observation['dateSort'] >= datetime_from and date_to == "":
                observation_list.append(observation)
            elif observation['dateSort'] >= datetime_from and observation['dateSort'] <= datetime_to:
                observation_list.append(observation)
            else:
                continue

        statements = client.resources(
            'MedicationRequest').search(subject=patient_reference)
        statements_list = []
        for s in statements:
            statement = {}
            statement['typeString'] = "Lekarstwo"
            statement['value'] = s['medicationCodeableConcept']['coding'][0]['display']
            statement_date_string = s['authoredOn']
            statement['date'] = parser.parse(
                statement_date_string).strftime("%d/%m/%Y, %H:%M:%S")
            statement['dateSort'] = parser.parse(statement_date_string)
            if statement['dateSort'] <= datetime_to and date_from == "":
                statements_list.append(statement)
            elif statement['dateSort'] >= datetime_from and date_to == "":
                statements_list.append(statement)
            elif statement['dateSort'] >= datetime_from and statement['dateSort'] <= datetime_to:
                statements_list.append(statement)
            else:
                continue
            print("test" + statement['dateSort'].strftime("%d/%m/%Y, %H:%M:%S"))
        medical_data_list = observation_list + statements_list
        medical_data_list = sorted(medical_data_list, key=lambda d: d['dateSort'], reverse=True)

        return render_template("patientData.html", patient_data=patient, medical_data=medical_data_list)


if __name__ == "__main__":
    # patient = client.reference(
    #     'Patient', '31191928-6acb-4d73-931c-e601cc3a13fa')
    # statements = client.resources('Observation').search(subject=patient)
    # for s in statements:
    #     print(s.to_resource()['issued'])
    
    app.run(debug=True)
