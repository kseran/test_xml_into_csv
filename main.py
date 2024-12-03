import logging
import os
import shutil
import sys
from xml.etree import ElementTree
import csv

log_dir = 'log'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'processing.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def xml_into_csv(file_path: str) -> None:
    if not file_path.lower().endswith(".xml"):
        logging.error(f"Файл {file_path} не является xml файлом. Обработка не возможна")
        shutil.move(file_path, os.path.join('bad', os.path.basename(file_path)))
        return
    # Чтение XML из файла
    tree = ElementTree.parse(source=file_path)
    root = tree.getroot()
    encoding_file = get_xml_encoding(file_path=file_path)

    # Получение текста из XML
    text = ElementTree.tostring(root, encoding='unicode')

    # Преобразование текста в кодировку Windows-1251
    encoded_text = text.encode(encoding_file)

    # Вывод закодированного текста
    print(encoded_text.decode(encoding_file))  # Декодируем для корректного вывода в терминал

    with open(file_path.replace('.xml', '.csv'), 'a', newline='',
              encoding='utf=8') as f:  # здесь записываем данные в конечный csv
        writer = csv.writer(f, delimiter=';')


    # отправлем файл в архив
    shutil.move(file_path, os.path.join('arh', os.path.basename(file_path)))
    logging.info(f"Файл {file_path} успешно обработан.")


def get_xml_encoding(file_path: str) -> str | None:
    with open(file_path, 'rb') as f:  # Открываем файл в двоичном режиме
        first_line = f.readline()  # Читаем первую строку
        # Пробуем найти кодировку в заголовке
        if b'<?xml' in first_line:
            start = first_line.find(b'encoding="') + len(b'encoding="')
            end = first_line.find(b'"', start)
            if start != -1 and end != -1:
                encoding_file = first_line[start:end].decode('utf-8')  # Декодируем в UTF-8
                return encoding_file
    return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Неверная команда запуска. Используйте: python main.py <путь к xml-файлу>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print("Файл не найден.")
        sys.exit(1)
    xml_into_csv(file_path=file_path)

