from .morning_star import *
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

class SpreadSheetComparation:
    """
    Populates a spreedsheet file using Morninstar data.
    Made for fundamental analysis
    """
    
    path: str = 'assets/base-sheet.xlsx'
    workbook: Workbook = None
    performanceIds: list
    symbols: list
    outputFilename: str = 'comparation.xlsx'
    initialColumn: int = 3
    # initialRow: int = 3
    rowMap: dict = {
        'currentRatio': 3,
        'quickRatio': 4,
        'debtToEquity': 6,
        'inventoryTurnover': 7,
        'daysInventory': 8,
        'AssetTurnover': 9,
        'roe': 10,
        'netMargin': 11,
        'PER': 12,
        'PCF': 13,
        'PS': 14,
        'PBV': 15,
        'price': 18,
        'PER-5yr': 26,
        'PCF-5yr': 29,
        'PS-5yr': 32,
        'PBV-5yr': 35,
    }

    def __init__(self):
        print("Loading...")
        self.workbook = load_workbook(filename=self.path)

    def do(self):
        sheet: Worksheet = self.workbook.active
        self._loadSymbolsAsHeaders(sheet)
        self._loadOverviewData(sheet)
        self.workbook.save(filename=self.outputFilename)
        print("Finished")

    def _loadSymbolsAsHeaders(self, sheet: Worksheet):
        titleRow = 2
        for key, symbol in enumerate(self.symbols):
            sheet.cell(row=titleRow, column=self.initialColumn + key).value = symbol
    
    def _loadOverviewData(self, sheet: Worksheet):
        for key, symbol in enumerate(self.symbols):
            response = getOverview(symbol)

            sheet.cell(
                row=self.rowMap['currentRatio'], 
                column=self.initialColumn + key
            ).value = response['financialHealth']['currentRatio']
            sheet.cell(
                row=self.rowMap['quickRatio'], 
                column=self.initialColumn + key
            ).value = response['financialHealth']['quickRatio']
            sheet.cell(
                row=self.rowMap['debtToEquity'], 
                column=self.initialColumn + key
            ).value = response['financialHealth']['debtToEquity']

            sheet.cell(
                row=self.rowMap['roe'], 
                column=self.initialColumn + key
            ).value = response['efficiencyRatio']['returnOnEquity']
            sheet.cell(
                row=self.rowMap['netMargin'], 
                column=self.initialColumn + key
            ).value = response['profitabilityRatio']['netMargin']

            sheet.cell(
                row=self.rowMap['PER'], 
                column=self.initialColumn + key
            ).value = response['valuationRatio']['priceToEPS']
            sheet.cell(
                row=self.rowMap['PCF'], 
                column=self.initialColumn + key
            ).value = response['valuationRatio']['priceToCashFlow']
            sheet.cell(
                row=self.rowMap['PS'], 
                column=self.initialColumn + key
            ).value = response['valuationRatio']['priceToSales']
            sheet.cell(
                row=self.rowMap['PBV'], 
                column=self.initialColumn + key
            ).value = response['valuationRatio']['priceToBook']