import requests

URL = "https://api.ibb.gov.tr/iett/AracAnaVeri/AracOzellik.asmx"

USERNAME = "KULLANICI_ADIN"
PASSWORD = "SIFREN"

soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope
    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:tem="http://tempuri.org/">

    <soap:Header>
        <tem:AuthHeader>
            <tem:Username>{USERNAME}</tem:Username>
            <tem:Password>{PASSWORD}</tem:Password>
        </tem:AuthHeader>
    </soap:Header>

    <soap:Body>
        <tem:GetAracOzellikleriIETT_json>
            <tem:KapiNo></tem:KapiNo>
        </tem:GetAracOzellikleriIETT_json>
    </soap:Body>

</soap:Envelope>
"""

headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": '"http://tempuri.org/GetAracOzellikleriIETT_json"'
}

response = requests.post(
    URL,
    data=soap_body.encode("utf-8"),
    headers=headers,
    timeout=60
)

print("HTTP DURUMU:", response.status_code)
print()
print(response.text)