import requests

REPETIER_SERVER_URL = "http://localhost:3344/api/v1/printer/ender_3_pro/print"
API_KEY = "61b8ef42-1595-4df1-949c-845d125515e4"

def get_temperature_info():
    try:
        url = f"{REPETIER_SERVER_URL}/api/v1/printer/ender_3_pro/temperatures"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error getting temperature info from Repetier Server. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error getting temperature info from Repetier Server: {e}")
        return None

# Другие функции управления температурой (если есть)

# Пример использования
temperature_info = get_temperature_info()
if temperature_info:
    print(temperature_info)
else:
    print("Failed to get temperature info.")
