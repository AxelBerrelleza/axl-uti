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
        key = 0
        response = {
            'valuationRatio': {'asOfDate': '2025-02-27', 'priceToBook': 9.643202, 'priceToCashFlow': 23.364486, 'priceToSales': 11.198208, 'priceToEPS': 31.630137},
            'growthRatio': {'reportDate': '2024-06-30', 'revenue': 0.134006, 'operatingIncome': 0.161067, 'netIncome': 0.128841, 'eps': 0.135957},
            'financialHealth': {'reportDate': '2024-12-31', 'quickRatio': 1.099713, 'currentRatio': 1.35082, 'debtToEquity': 0.205567},
            'efficiencyRatio': {'reportDate': '2024-12-31', 'returnOnAssets': 0.184677, 'returnOnEquity': 0.342907, 'returnOnInvestedCapital': 0.268562},
            'profitabilityRatio': {'reportDate': '2024-12-31', 'interestCoverage': 43.439671, 'netMargin': 0.354275},
            'keyStatsQuoteJson': {
                'revenue3YearGrowth': {'stockValue': '13.4000', 'indAvg': '13.2300'},
                'netIncome3YearGrowth': {'stockValue': '12.8800', 'indAvg': '14.4900'},
                'operatingMarginTTM': {'stockValue': '44.9600', 'indAvg': '30.0000'},
                'netMarginTTM': {'stockValue': '35.4300', 'indAvg': '23.0700'},
                'roaTTM': {'stockValue': '18.4700', 'indAvg': '11.3600'},
                'roeTTM': {'stockValue': '34.2900', 'indAvg': '28.7600'},
                'debitToEquity': {'stockValue': '0.1882', 'indAvg': '0.5167'},
                'freeCashFlow': {'cashFlowTTM': '70031000000', 'date': '2024-12-31T06:00:00.000'}
            }
        }

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