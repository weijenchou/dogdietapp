from datetime import datetime

def calculate_RER(weight):
    # 計算基礎能量需求 (RER)
    return 70 * (weight ** 0.75)

def calculate_DER(RER, AF):
    # 計算日常能量需求 (DER)
    return RER * AF

def calculate_water_intake(weight):
    # 計算狗狗的水量需求
    min_water = weight * 50  # 最低水量 (ml)
    max_water = weight * 70  # 最高水量 (ml)
    return min_water, max_water

def get_AF():
    # 請使用者選擇狗的狀態，根據狀態給出對應的需求因子(AF)
    print("選擇狗的狀態:")
    print("1. 正在發育的幼犬（4個月以下）: 2.5-3.0")
    print("2. 正在發育的幼犬（4個月-1歲）: 2.0-2.5")
    print("3. 結紮成年犬（1-7歲）: 1.4-1.6")
    print("4. 未結紮成年犬（1-7歲）: 1.6-1.8")
    print("5. 輕度減肥成年犬: 1.2-1.4")
    print("6. 重度減肥成年犬: 1.0-1.2")
    print("7. 過瘦成年犬: 1.6-2.0")
    print("8. 輕度活動量: 1.2-1.4")
    print("9. 劇烈活動量: 2.0-2.5")
    print("10. 高齡犬: 1.2-1.4")
    print("11. 懷孕中的狗媽媽: 1.8-2.0")
    print("12. 哺乳中的狗媽媽: 2.2-2.5")
    print("13. 生病成年犬: 1.0-1.5")

    choice = input("請選擇狀態（輸入對應數字）: ")

    # 根據選擇返回對應的需求因子區間
    if choice == '1':
        return (2.5, 3.0)  # 區間
    elif choice == '2':
        return (2.0, 2.5)
    elif choice == '3':
        return (1.4, 1.6)
    elif choice == '4':
        return (1.6, 1.8)
    elif choice == '5':
        return (1.2, 1.4)
    elif choice == '6':
        return (1.0, 1.2)
    elif choice == '7':
        return (1.6, 2.0)
    elif choice == '8':
        return (1.2, 1.4)
    elif choice == '9':
        return (2.0, 2.5)
    elif choice == '10':
        return (1.2, 1.4)
    elif choice == '11':
        return (1.8, 2.0)
    elif choice == '12':
        return (2.2, 2.5)
    elif choice == '13':
        return (1.0, 1.5)
    else:
        print("選擇錯誤，請重新選擇。")
        return get_AF()

def calculate_age(birth_date):
    # 計算狗狗的年齡和月齡
    today = datetime.today()
    birth_date = datetime.strptime(birth_date, '%Y-%m-%d')  # 解析生日字符串
    age_years = today.year - birth_date.year
    age_months = today.month - birth_date.month

    # 如果當前月日比生日月日早，則需要調整年齡和月齡
    if age_months < 0:
        age_years -= 1
        age_months += 12

    return age_years, age_months

def main():

    # 使用者輸入狗的名字和生日
    dog_name = input("請輸入狗的名字: ")
    dog_birthday = input("請輸入狗的生日（格式：YYYY-MM-DD）: ")
    
    # 計算狗的年齡和月齡
    dog_years, dog_months = calculate_age(dog_birthday)

    # 使用者輸入狗的體重
    weight = float(input("請輸入狗的體重（公斤）: "))
    
    # 計算 RER
    RER = calculate_RER(weight)
    
    # 讓使用者選擇狗的狀態，並計算 DER
    AF_min, AF_max = get_AF()  # 取得需求因子的區間
    DER_min = calculate_DER(RER, AF_min)
    DER_max = calculate_DER(RER, AF_max)

    # 計算狗狗的水量需求
    min_water, max_water = calculate_water_intake(weight)

    # 顯示結果
    print(f"\n名字: {dog_name}")
    print(f"生日: {dog_birthday}")
    print(f"年齡: {dog_years} 歲 {dog_months} 個月")
    print(f"體重: {weight} 公斤")
    print(f"基礎能量需求(RER): {RER:.2f} 大卡")
    print(f"日常能量需求 (DER) 範圍: {DER_min:.2f} - {DER_max:.2f} 大卡")
    print(f"每日喝水量: {min_water:.2f} ml - {max_water:.2f} ml")

if __name__ == "__main__":
    main()

