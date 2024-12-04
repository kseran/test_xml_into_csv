import logging
import os
import shutil
import sys
from datetime import datetime
from xml.etree import ElementTree
import csv

log_dir = 'log'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'processing.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def is_valid_csv_amount(amount_str):
    """Check that the amount is a positive number with two decimal places."""
    try:
        amount = float(amount_str)
        if amount < 0 or not (amount_str.endswith('.00') or amount_str.endswith('.01') or amount_str.endswith('.99')):
            return False
        return True
    except ValueError:
        return False


def is_valid_period(period_str):
    """Check the period format MMYYYY."""
    if len(period_str) == 6 and period_str.isdigit():
        return True
    return False


def xml_into_csv(file_path: str) -> None: #TODO пройтись по тз ещё раз и доделать
    if not file_path.lower().endswith(".xml"):
        logging.error(f"Файл {file_path} не является xml файлом. Обработка не возможна")
        os.makedirs('bad', exist_ok=True)
        shutil.move(file_path, os.path.join('bad', os.path.basename(file_path)))
        return
    # Чтение XML из файла
    tree = ElementTree.parse(source=file_path)
    root = tree.getroot()
    encoding_file = get_xml_encoding(file_path=file_path)

    # отправлем файл в архив
    os.makedirs('arh', exist_ok=True)
    # shutil.move(file_path, os.path.join('arh', os.path.basename(file_path)))
    logging.info(f"Файл {file_path} успешно обработан.")

    with open(file_path.replace('.xml' and '.XML', '.csv'), 'a', newline='',
              encoding=encoding_file) as f:  # здесь записываем данные в конечный csv
        writer = csv.writer(f, delimiter=';')
        unique_records = set()
        payer_info = root[1]
        for record in payer_info:
            print(record.find('ЛицСч'))
            account_number = record.find('ЛицСч')
            full_name = record.find('ФИО')
            address = record.find('Адрес')
            period = record.find('Период')
            amount = record.find('Сумма')

            # If key attributes are missing
            if account_number is None or period is None:
                logging.warning(f"Row number  is missing one of the key attributes.")
                continue

            account_number = account_number.text if account_number is not None else ''
            full_name = full_name.text if full_name is not None else ''
            address = address.text if address is not None else ''
            period = period.text if period is not None else ''
            amount = amount.text if amount is not None else ''

            if not is_valid_period(period):
                logging.warning(f"Invalid period format: {period}. Row skipped.")

            if not is_valid_csv_amount(amount):
                logging.warning(f"Invalid amount format: {amount}. Row skipped.")

            unique_key = (account_number, period)
            if unique_key in unique_records:
                logging.warning(
                    f"Duplicate record: Account Number = {account_number}; Period = {period}. Record skipped.")

            unique_records.add(unique_key)

            validity_date = root[0].find('.//ДатаФайл').text
            if validity_date is None:
                validity_date = ''
            writer.writerow([
                os.path.basename(file_path),
                validity_date,
                account_number,
                full_name,
                address,
                period,
                amount
            ])


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
    xml_into_csv(file_path="input — копия.XML")  # для тестов, позже удалить

    if len(sys.argv) != 2:
        logging.error("Неверная команда запуска. Используйте: python main.py <путь к xml-файлу>")
        sys.exit(1)

    file_path = sys.argv[1]
    print(file_path)
    if not os.path.exists(file_path):
        print("Файл не найден.")
        sys.exit(1)
    xml_into_csv(file_path=file_path)
