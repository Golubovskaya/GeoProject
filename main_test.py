import requests
import allure
import pytest

GEOCODER_API_KEY = '31fcf0e2-cabc-49cb-9e51-a9b3298faa38'
SEARCH_API_KEY = '619dd07a-9566-4fdf-82e5-daf83421ceae'


@allure.feature('Геокодирование')
@allure.story('Получение геолокации по адресу')
def test_geocode_address():
    # Шаг 1: Сделать запрос по адресу
    address = "Санкт-Петербург, Невский проспект, дом 1"
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={GEOCODER_API_KEY}&geocode={address}&format=json"

    response = requests.get(url)

    # Проверка успешного ответа
    assert response.status_code == 200, "Не удалось получить данные по адресу"

    data = response.json()

    # Извлекаем координаты
    geo_object = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
    coordinates = geo_object['Point']['pos']

    assert coordinates is not None, "Не удалось получить координаты"
    print(f"Координаты для {address}: {coordinates}")


@allure.feature('Поиск по организациям')
@allure.story('Поиск ближайших кафе')
def test_search_nearby_cafes():
    # Шаг 2: Поиск ближайших кафе по координатам
    coordinates = "30.360909,59.931058"  # Координаты из предыдущего теста
    url = f"https://search-maps.yandex.ru/v1/?apikey={SEARCH_API_KEY}&text=кафе&lang=ru_RU&ll={coordinates}&spn=0.01,0.01&type=biz&results=5"

    response = requests.get(url)

    # Проверка успешного ответа
    assert response.status_code == 200, "Не удалось получить данные о ближайших кафе"

    data = response.json()

    # Проверяем, что нашли хотя бы одно кафе
    cafes = data['features']
    assert len(cafes) > 0, "Не удалось найти ближайшие кафе"

    # Извлекаем название первого кафе
    first_cafe = cafes[0]['properties']['CompanyMetaData']['name']
    print(f"Название первого ближайшего кафе: {first_cafe}")

    assert first_cafe is not None, "Название первого кафе отсутствует"


@allure.feature('Поиск по организациям')
@allure.story('Поиск по URI кафе')
def test_search_by_uri():
    # Шаг 3: Поиск по URI кафе
    cafe_uri = "ymapsbm1://org?oid=164650033188"  # Пример URI кафе
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={GEOCODER_API_KEY}&uri={cafe_uri}&format=json"

    response = requests.get(url)

    # Проверка успешного ответа
    assert response.status_code == 200, "Не удалось получить данные по URI"

    data = response.json()
    geo_object = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

    # Проверка, что найдено правильное кафе
    actual_name = geo_object['metaDataProperty']['GeocoderMetaData']['text']
    print(f"Полученное название: {actual_name}")
    expected_name = "Baggins Coffee"  # Обновлённое название

    assert expected_name in actual_name, f"Неверное кафе: ожидалось {expected_name}, но получено {actual_name}"


@allure.feature('Геокодирование')
@allure.story('Негативный тест: неверный адрес')
def test_invalid_address():
    # Шаг 4: Проверка на неверный адрес
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={GEOCODER_API_KEY}&geocode=Неизвестный+адрес&format=json"
    response = requests.get(url)

    # Проверка успешного ответа
    assert response.status_code == 200, "Запрос завершился ошибкой"

    # Проверка, что не удалось найти данные по неверному адресу
    data = response.json()
    found_objects = data['response']['GeoObjectCollection']['featureMember']

    # Проверяем, что ни один найденный объект не является конкретным адресом (например, должен быть географическим объектом)
    assert all(
        obj['GeoObject']['metaDataProperty']['GeocoderMetaData']['kind'] != 'house'
        for obj in found_objects
    ), "Найдены данные для конкретного адреса, хотя ожидался некорректный запрос"
