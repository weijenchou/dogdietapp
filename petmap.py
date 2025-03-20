import os
from pprint import pprint
import requests
import json
import geocoder
from dotenv import load_dotenv


def get_place_detail_fields():
    return [
        'places.location',
        'places.displayName',
        'places.formattedAddress',
        'places.reviews',
        'places.rating',
        'places.allowsDogs'
    ]


def search_place_by_name(api_key, text_query, fields=get_place_detail_fields()):
    URL = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": ",".join(fields)
    }

    payload = {
        "textQuery": text_query
    }

    response = requests.post(URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        results = response.json().get("places", [])
        if results:
            return results
        else:
            print("❌ 没有找到符合条件的地点。")
    else:
        print(f"❌ 请求失败，状态码: {response.status_code}, 错误信息: {response.text}")

    return list()


def search_nearby_places(api_key, lat, lon, fields=get_place_detail_fields(), radius=1000, place_type=['restaurant'], max_count=20):
    URL = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": ",".join(fields)
    }

    payload = {
        "includedTypes": place_type,
        "maxResultCount": max_count,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lon},
                "radius": radius
            }
        }
    }

    response = requests.post(URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        results = response.json()
        return results.get("places", [])
    else:
        print(f"❌ 请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
        return list()


def get_location(API_KEY):
    """
    讓使用者選擇搜尋方式，並返回經度和緯度。
    選擇方式有兩種：
    1. 目前位置
    2. 輸入地標名稱
    """
    # 讓使用者選擇
    choice = input("請選擇搜尋方式(輸入1或2):\n1. 目前位置\n2. 輸入地標名稱\n選擇 (1/2): ").strip()

    if choice == '1':
        # 使用 geocoder 獲取目前位置
        g = geocoder.ip('me')
        LAT, LON = g.latlng
        if LAT is None or LON is None:
            print("❌ 無法獲取當前位置，請確認您的網路連接或位置服務是否正常。")
            exit()
        print(f"📍 目前位置：經度 {LAT}, 緯度 {LON}")
        return LAT, LON
    elif choice == '2':
        # 使用者輸入地標名稱
        place_name = input("請輸入地標名稱: ").strip()
        # 搜尋該地標
        places = search_place_by_name(API_KEY, place_name)
        if not places:
            print("❌ 未找到該地標的相關資訊。")
            exit()

        location = places[0]['location']
        LAT, LON = location['latitude'], location['longitude']
        print(f"📍 {place_name} 的經度: {LAT}, 緯度: {LON}")
        return LAT, LON
    else:
        print("❌ 無效選擇，請重新運行程式。")
        exit()



if __name__ == "__main__":
    load_dotenv('information.env')
    API_KEY = os.getenv("GOOGLE_MAP_API_KEY")

    LAT, LON = get_location(API_KEY)

    # 接下來你可以利用 LAT 和 LON 來進行其他的搜尋操作
    places = search_nearby_places(API_KEY, LAT, LON, max_count=20, place_type=['dog_cafe', 'cat_cafe', 'restaurant'])

    for place in places:
        is_allow_dogs = place.get('allowsDogs', False)
        if is_allow_dogs:
            print(f"🍴 餐廳: {place.get('displayName', {}).get('text', '未知')}")
            print(f"⭐ 評分: {place.get('rating', '無評分')}")
            print(f"📍 地址: {place.get('formattedAddress', '地址未知')}")
            print()





