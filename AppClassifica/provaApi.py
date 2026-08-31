import http.client

conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "ad91af2ed7msh7c8ff1792ea7129p19fd69jsn811dc305a3b1",
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
}

conn.request("GET", "/v3/fixtures/headtohead?h2h=33-34", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))