import json
import time
import urllib.request
import urllib.parse


# 3. Создание модели WeatherData
class WeatherData:
    def __init__(self, city, temp, country):
        self.city = city
        self.temp = temp
        self.country = country

    # 4. Вывод полученной информации по каждому городу
    def __str__(self):
        return f"{self.city}, {self.country} {self.temp:+d}°C"


# 1. Функция загрузки списка городов из файла
def load_cities(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return [line.strip() for line in f if line.strip()]


# 2. Функция запроса к API
def fetch_weather_API(city: str) -> dict | None:
    safe_city = urllib.parse.quote(city)
    url = f'https://wttr.in/{safe_city}?format=j1'
    req = urllib.request.Request(url, headers={"User-Agent": "curl/7.88.1"})

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Ошибка при получении данных по {city}: {e}")
        return None

# Функция для записи данных в модель WeatherData
def parse_weather(city: str, city_data: dict) -> WeatherData | None:
    try:
        temp = int(city_data["current_condition"][0]["temp_C"])
        country = city_data["nearest_area"][0]["country"][0]["value"]
        return WeatherData(city=city, temp=temp, country=country)
    except Exception as e:
        print(f"Не удалось распарсить данные по {city}: {e}")
        return None

# Функция группировки по стрнам
def group_by_country(weather_list: list[WeatherData]) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = {}

    for wd in weather_list:
        groups.setdefault(wd.country, []).append(wd.temp)
    return groups

# 5. Функция для вывода статы по каждой стране
def print_country_stats(country_stats: dict[str, list[int]]) -> None:
    for country, temp in country_stats.items():
        cities_count = len(temp)
        avg_temp = sum(temp) / len(temp)
        min_temp = min(temp)
        max_temp = max(temp)

        print(
            f"{country} - {cities_count} "
            f"{'city' if cities_count == 1 else 'cities'}, "
            f"avg: {avg_temp:+.1f}°C, "
            f"min: {min_temp:+d}°C, "
            f"max: {max_temp:+d}°C"
        )


if __name__ == "__main__":
    # 1. Загрузка списка городов из файла
    cities = load_cities("Cities.txt")
    cities = list(dict.fromkeys(cities))

    # 3. Модель WeatherData
    weather_list: list[WeatherData] = []

    print("Cities weather")
    for city in cities:
        # 2. Получение данных через API
        city_data = fetch_weather_API(city)
        if city_data is None:
            print(f"{city}: пропуск (ошибка запроса)")
            time.sleep(0.5)
            continue

        wd = parse_weather(city, city_data)
        if wd is None:
            print(f"{city}: пропуск (ошибка парсинга)")
            time.sleep(0.5)
            continue

        weather_list.append(wd)
        print(wd) # 4. Вывод информации по каждому городу

        time.sleep(0.5)


    # 5. Группировка и статистика по каждой стране
    print("\nCountry stats")
    weather_by_country = group_by_country(weather_list)
    print_country_stats(weather_by_country)