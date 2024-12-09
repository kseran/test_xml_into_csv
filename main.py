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


def is_valid_amount(amount_str: str) -> bool:
    try:
        number_characters = amount_str.split(".")[1]
        amount = float(amount_str)
        if amount > 0 and len(number_characters) == 2:
            return True
        return False
    except (ValueError, IndexError):
        return False


def is_valid_period(period_str: str) -> bool:
    if period_str is not None and len(period_str) == 6 and period_str.isdigit():
        return True
    return False


def get_xml_file_encoding(path: str) -> str | None:
    with open(path, 'rb') as f:
        first_line = f.readline()
        if b'<?xml' in first_line:
            start = first_line.find(b'encoding="') + len(b'encoding="')
            end = first_line.find(b'"', start)
            if start != -1 and end != -1:
                encoding_file = first_line[start:end].decode('utf-8')
                return encoding_file
    return None


def xml_into_csv(path: str) -> None:
    logging.info(f"Запушена обработка файла: {path}")
    if not path.lower().endswith(".xml"):
        logging.error(f"Файл {path} не является xml файлом. Обработка не возможна")
        os.makedirs('bad', exist_ok=True)
        shutil.move(path, os.path.join('bad', os.path.basename(path)))
        return None
    tree = ElementTree.parse(source=path)
    root = tree.getroot()
    encoding_file = get_xml_file_encoding(path=path)

    with open(path.replace('.xml' or '.XML', '.csv'), 'a', newline='',
              encoding=encoding_file) as f:
        logging.info(f"Файл {path.replace('.xml' or '.XML', '.csv')} успешно создан. Идёт заполнение.")
        writer = csv.writer(f, delimiter=';')
        unique_records = set()
        for idx, record in enumerate(root[1].findall('Плательщик')):
            account_number = record.find('ЛицСч').text or ''
            full_name = record.find('ФИО').text or ''
            address = record.find('Адрес').text or ''
            period = record.find('Период').text or ''
            amount = record.find('Сумма').text or ''

            if not account_number or not period:
                logging.warning(f"Строка номер {idx} не имеет одного из ключевых реквизитов")
                continue

            if not is_valid_period(period):
                logging.warning(f"Строка номер {idx} неправильный формат периода: {period}. Запись пропущена.")
                continue

            if not is_valid_amount(amount):
                logging.warning(f"Строка номер {idx} не соответствует формат суммы. Запись пропущена.")
                continue

            unique_key = (account_number, period)
            if unique_key in unique_records:
                logging.warning(
                    f"Найден дубликат записи, лицевой счёт = {account_number}; период = {period}. Запись пропущена.")
                continue

            validity_date = root[0].find('.//ДатаФайл').text or ''
            writer.writerow([
                os.path.basename(path),
                validity_date,
                account_number,
                full_name,
                address,
                period,
                amount
            ])

            unique_records.add(unique_key)

    os.makedirs('arh', exist_ok=True)
    shutil.move(path, os.path.join('arh', os.path.basename(path)))
    logging.info(f"Файл {path} успешно обработан.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Неверная команда запуска. Используйте: python main.py <путь к xml-файлу>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        logging.error(f"Файл {file_path} не найден.")
        sys.exit(1)
    xml_into_csv(path=file_path)
