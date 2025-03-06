import pytest
from typer.testing import CliRunner
from logging import getLogger
from commands.stocks import stocks_app, Endpoints
from commands.tests.fixtures import APIResponses
from commands.stocks.SpreedSheetComparation import SpreadSheetComparation
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

runner = CliRunner()
logger = getLogger(__name__)

def test_help():
    result = runner.invoke(stocks_app, ['comparator', '--help'])
    assert result.exit_code == 0
    assert result.stdout != None

def test_command(requests_mock):
    requests_mock.get(Endpoints.OVERVIEW, json=APIResponses.MS.OVERVIEW)
    symbols = ['GOOGL', 'AMZN']
    result = runner.invoke(stocks_app, ['comparator', *symbols])
    
    print(result)
    assert 'Loading' in result.stdout
    assert 'Finished' in result.stdout
    
    xlDoc = load_workbook(filename='comparation.xlsx', data_only=True)
    sheet: Worksheet = xlDoc.active
    for key, symbol in enumerate(symbols):
        assert sheet.cell(row=2, column=SpreadSheetComparation.initialColumn + key).value == symbol
        
    for cells in sheet.iter_cols(min_col=SpreadSheetComparation.initialColumn, min_row=3, max_col=4, max_row=15):
        logger.info(list(( c.value for c in cells )))