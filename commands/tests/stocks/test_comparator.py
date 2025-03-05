import pytest
from typer.testing import CliRunner
from commands.stocks import stocks_app, Endpoints, getOverview
from commands.tests.fixtures import APIResponses

runner = CliRunner()

def test_help():
    result = runner.invoke(stocks_app, ['comparator', '--help'])
    assert result.exit_code == 0
    assert result.stdout != None

# def test_creation_of_xl_file():
def test_mock(requests_mock):
    requests_mock.get(Endpoints.OVERVIEW, json=APIResponses.MS.OVERVIEW)
    result = runner.invoke(stocks_app, ['comparator', 'GOOGL', 'AMZN'])
    
    print(result)
    assert 'Loading' in result.stdout
    assert 'Finished' in result.stdout