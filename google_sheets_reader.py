from oauth2client.service_account import ServiceAccountCredentials
import gspread
from settings import account_credentials_file
import string


class GoogleSheetsReader:
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(account_credentials_file, scope)
    gc = gspread.authorize(credentials)
    alphabet = string.ascii_uppercase

    @staticmethod
    def get_all_records(table_url: str, sheet=0):
        table = GoogleSheetsReader.gc.open_by_url(table_url)
        worksheet = table.get_worksheet(sheet)
        return worksheet.get_all_records()

    @staticmethod
    def get_all_values(table_url: str, sheet=0):
        table = GoogleSheetsReader.gc.open_by_url(table_url)
        worksheet = table.get_worksheet(sheet)
        return worksheet.get_all_values()

    @staticmethod
    def get_worksheet(table_url: str, sheet=0):
        table = GoogleSheetsReader.gc.open_by_url(table_url)
        worksheet = table.get_worksheet(sheet)
        return worksheet

    @staticmethod
    def create_and_return_worksheet(table_url: str, sheet_title: str, rows: str, cols: str):
        table = GoogleSheetsReader.gc.open_by_url(table_url)
        try:
            worksheet = table.worksheet(sheet_title)
            return worksheet
        except:
            pass
        worksheet = table.add_worksheet(title=sheet_title, rows=rows, cols=cols)
        return worksheet

    @staticmethod
    def create_header(worksheet, header):
        header_len = len(header)
        begin = f'{GoogleSheetsReader.alphabet[0]}1'
        end = f'{GoogleSheetsReader.alphabet[header_len - 1]}1'
        cells_list = worksheet.range(f'{begin}:{end}')
        for i, cell in enumerate(cells_list):
            cell.value = str(header[i])
        worksheet.update_cells(cells_list)
