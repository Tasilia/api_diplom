import requests


class DiskClient:
    """Клиент для работы с API Яндекс.Диск

    Attributes:
        __token: OAuth-токен для авторизации в API.
    """

    BASE_URL = "https://cloud-api.yandex.net"  # Базовый URL API
    BASE_RESOURCE = "PD-162"  # Целевая папка на диске (наименование группы)

    SUCCESS_STATUS = "success"  # Успешный статус выполнения асинхронной операции
    IN_PROGRESS_STATUS = (
        "in-progress"  #  Статус выполнения асинхронной операции - операция выполняется
    )
    FAILED_STATUS = "failed"  # Ошибочный статус выполнения асинхронной операции

    def __init__(self, token):
        """
        Args:
            token: OAuth-токен, полученный в Яндекс.OAuth.
        """
        self.__token = token

    def _get_headers(self):
        """Формирует заголовки для HTTP-запросов к API.

        Returns:
            Словарь с заголовками, содержащими Content-Type и OAuth-токен.
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"OAuth {self.__token}",
        }

    def get_resources(self, url=None, fields=None):
        """Возвращает метаинформацию о файле или каталоге по пути url на Яндекс.Диске.

        Если путь не указан, возвращает содержимое корневой папки.

        Args:
            url: Путь к ресурсу на Диске (например, "/PD-162"). Если None,
                запрашивается корень Диска.
            fields: Строка со списком возвращаемых атрибутов.

        Returns:
            Словарь с метаинформацией о ресурсе.

        Raises:
            requests.HTTPError: Если API вернул статус ошибки.
        """
        path = "/" if not url else url
        params = {"path": path}
        if fields:
            params.update({"fields": fields})
        resp = requests.get(
            f"{self.BASE_URL}/v1/disk/resources",
            params=params,
            headers=self._get_headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def create_folder(self):
        """Создаёт целевую папку для загрузки файлов на Яндекс.Диске.

        Имя папки берётся из константы BASE_RESOURCE.

        Raises:
            requests.HTTPError: Если API вернул статус ошибки.
        """
        params = {"path": f"/{self.BASE_RESOURCE}"}
        resp = requests.put(
            f"{self.BASE_URL}/v1/disk/resources",
            params=params,
            headers=self._get_headers(),
        )
        resp.raise_for_status()

    def upload_file(self, file_name, file_url):
        """Загружает файл на Яндекс.Диск по внешней ссылке.

        Файл скачивается сервером Яндекса по указанному URL и кладётся
        в целевую папку BASE_RESOURCE под именем file_name.

        Args:
            file_name: Имя, под которым файл будет сохранён на Диске.
            file_url: Публичный URL файла, который нужно скачать.

        Returns:
            Ссылка (href) на статус асинхронной операции загрузки.
            По ней можно отслеживать результат через get_operation_status.

        Raises:
            requests.HTTPError: Если API вернул статус ошибки.
        """
        params = {"path": f"/{self.BASE_RESOURCE}/{file_name}", "url": file_url}
        resp = requests.post(
            f"{self.BASE_URL}/v1/disk/resources/upload",
            params=params,
            headers=self._get_headers(),
        )
        resp.raise_for_status()
        return resp.json()["href"]

    def get_operation_status(self, url):
        """Возвращает статус асинхронной операции на Яндекс.Диске.

        Args:
            url: Ссылка на статус операции.

        Returns:
            Строка со статусом операции: "success" (успешно),
            "in-progress" (выполняется) или "failed" (провалилась).
            None, если поле status отсутствует в ответе.

        Raises:
            requests.HTTPError: Если API вернул статус ошибки.
        """
        resp = requests.get(
            url,
            headers=self._get_headers(),
        )
        resp.raise_for_status()
        return resp.json().get("status")
