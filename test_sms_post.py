import requests

data = {
    "Body": "There was a robbery near Kaduna tollgate",
    "From": "+2348123456789"
}

res = requests.post("http://127.0.0.1:5000/sms", data=data)
print("Response:", res.text)
