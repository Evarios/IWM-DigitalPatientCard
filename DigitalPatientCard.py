from flask import Flask, render_template
from fhirpy import SyncFHIRClient

# setup
app = Flask(__name__)
client = SyncFHIRClient("http://localhost:8080/baseR4")

@app.route("/")
def hello():
    return render_template("base.html")


@app.route("/patientsList")
def patients():
    resources = client.resources('Patient')
    patients = resources.fetch()
    patients_list = []
    for pt in patients:
        patient = {
            'name': pt['name'][0].given[0],
            'surname': pt['name'][0].family,
            'id': pt['id']
        }
        patients_list.append(patient)
    return render_template("patientsList.html", patients=patients_list)
    

if __name__ == "__main__":
    app.run(debug=True)