import os
import requests

THRESHOLD = 4.25
URL = 'https://api.api-ninjas.com/v1/mortgagerate'

# 2. Industry Standard Adjustments (for 740+ FICO)
REFY_PREMIUM = 0.15     # Refinances usually cost ~0.15% more than purchases
JUMBO_SPREAD = 0.25     # Jumbo fixed is usually ~0.25% higher than conforming

def get_refi_estimates():
  API_KEY = os.environ.get("NINJIA_API_KEY")
  response = requests.get(URL, headers={'X-Api-Key': API_KEY})
  
  if response.status_code == 200:
    # API Ninjas returns a list/object where 'frm_30' is the benchmark
    data = response.json()[0]['data']
    print(data)
    base_rate = float(data['frm_30'])
    date_updated = data['week']
  
    # Calculation Logic
    conforming_refi = base_rate + REFY_PREMIUM
    jumbo_refi = conforming_refi + JUMBO_SPREAD
    jumbo_refi_7arm = jumbo_refi - 0.75
    return date_updated, jumbo_refi_7arm

def send_message(subject,text):
  api_key = os.environ.get("API_KEY")
  email_address = os.environ.get("EMAIL_ADDR")
  uri = os.environ.get("MAILGUN_URI")
  sender = os.environ.get("MAILGUN_SENDER")
  return requests.post(
    uri,
    auth=("api", os.getenv('API_KEY', api_key)),
    data={"from": sender,
    "to": email_address,
      "subject": subject,
      "text": text})

def send_alert(date_updated, jumbo_refi_7arm ):  
  return send_message(subject,text)


date_updated, jumbo_refi_7arm = get_refi_estimates()

if jumbo_refi_7arm < THRESHOLD:  
  subject = "GOOD MORTAGATE RATE ALERT"
  text = f"--- Refinance Estimates (Week of {date_updated}) --- \n"+f"30Y Jumbo Refi ARM:        {jumbo_refi_7arm:.3f}%"
  print(send_message(subject,text))
else:
  print("nothing to send")
  
