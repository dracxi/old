import requests
import os

url = os.environ['webhook_url']

#for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
data = {"content": "message content", "username": "custom username"}


def webhook(data):
  result = requests.post(url, json=data)
  try:
    result.raise_for_status()
  except requests.exceptions.HTTPError as err:
    print(err)
  else:
    print("Payload delivered successfully, code {}.".format(
      result.status_code))
