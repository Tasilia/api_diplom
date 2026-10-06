from disk_client import DiskClient
from time import sleep
import json


def create_cat_url(text):
    """Формирует ссылку на изображение кота для дальнейшего скачивания.

    Args:
        text: Текст, который будет сгенерирован на изображении.

    Returns:
        Строка с url на api /cat/says/:text
    """
    BASE_URL = "https://cataas.com"
    return f"{BASE_URL}/cat/says/{text}"


if __name__ == "__main__":
    file_name = input("Введите текст для картинки: ")
    token = input("Введите токен для Яндекс.Полигона: ")
    disk_client = DiskClient(token)
    print("Запрашиваем информацию о ресурсах")
    items = disk_client.get_resources().get("_embedded", {}).get("items")
    if any(item.get("name") == disk_client.BASE_RESOURCE for item in items):
        print(f"Целевая папка {disk_client.BASE_RESOURCE} уже существует.")
    else:
        print(f"Создаем целевую папку {disk_client.BASE_RESOURCE}")
        disk_client.create_folder()
    cat_url = create_cat_url(file_name)
    print(f"Загружаем файл {file_name} в директорию /{disk_client.BASE_RESOURCE}")
    url = disk_client.upload_file(file_name, cat_url)
    status = disk_client.IN_PROGRESS_STATUS
    while status == disk_client.IN_PROGRESS_STATUS:
        print("Файл в процессе загрузки.")
        sleep(1)
        status = disk_client.get_operation_status(url)
    if status == disk_client.SUCCESS_STATUS:
        print("Файл успешно загружен.")
        print("Запрашиваем инфомацию о размере загруженного файла.")
        file_info = disk_client.get_resources(
            url=f"/{disk_client.BASE_RESOURCE}/{file_name}", fields="size"
        )
        print(file_info)
        file_info_name = f"{file_name}_info.json"
        with open(file_info_name, "w") as f:
            f.write(json.dumps(file_info))
        print(
            f"Инфомация о размере загруженного файла {file_name} записана в файл {file_info_name}"
        )
    elif status == disk_client.FAILED_STATUS:
        print("Ошибка загрузки файла.")
    else:
        print("Статус загрузки неизвестен.")
