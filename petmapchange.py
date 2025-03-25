# petmap.py
import os
import requests
import json
import geocoder
from dotenv import load_dotenv

# 載入環境變數
load_dotenv('information.env')
API_KEY = os.getenv("GOOGLE_MAP_API_KEY")

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
        return results if results else []
    return []

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
        return response.json().get("places", [])
    return []

def get_location_by_choice(choice, place_name=None):
    """根據用戶選擇返回經緯度"""
    if choice == "1":
        g = geocoder.ip('me')
        LAT, LON = g.latlng
        if LAT is None or LON is None:
            return None, None
        return LAT, LON
    elif choice == "2" and place_name:
        places = search_place_by_name(API_KEY, place_name)
        if not places:
            return None, None
        location = places[0]['location']
        return location['latitude'], location['longitude']
    return None, None

def search_pet_restaurants(choice, place_name=None):
    """搜尋寵物餐廳並返回結果"""
    LAT, LON = get_location_by_choice(choice, place_name)
    if LAT is None or LON is None:
        if choice == "1":
            return "無法獲取當前位置，請確認您的網路連接或位置服務是否正常。"
        elif choice == "2":
            return f"未找到 '{place_name}' 的相關資訊。"
        return "無效的搜尋方式。"

    places = search_nearby_places(API_KEY, LAT, LON, max_count=20, place_type=['dog_cafe', 'cat_cafe', 'restaurant'])
    response = ""
    dog_friendly_count = 0

    for place in places:
        is_allow_dogs = place.get('allowsDogs', False)
        if is_allow_dogs:
            dog_friendly_count += 1
            response += f"🍴 餐廳: {place.get('displayName', {}).get('text', '未知')}\n"
            response += f"⭐ 評分: {place.get('rating', '無評分')}\n"
            response += f"📍 地址: {place.get('formattedAddress', '地址未知')}\n\n"

    if dog_friendly_count == 0:
        response = "附近沒有找到允許狗狗的餐廳。"
    else:
        response = f"找到 {dog_friendly_count} 家允許狗狗的餐廳：\n\n" + response
    return response