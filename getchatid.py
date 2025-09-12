import requests

TOKEN = "8329591563:AAHD3KFDCK7u3kkPqGfFzJLSVVZ-IIjhdgw"  # ton vrai token BotFather
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

resp = requests.get(url)
data = resp.json()
print(data)

if "result" in data and data["result"]:
    chat_id = data["result"][0]["message"]["chat"]["id"]
    print("Ton chat_id est :", chat_id)
else:
    print("⚠️ Aucun message trouvé. Envoie un message à ton bot et relance le script.")
