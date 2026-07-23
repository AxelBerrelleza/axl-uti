import logging

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from commands.errors import AxlError
from commands.stocks.comparator_adapter import FallbackAdapter, OverviewAdapter
from commands.stocks.errors import ComparatorError

from .morning_star import *

logging.basicConfig(filename="debug.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

USE_FALLBACK_ADAPTER = True


class SpreadSheetComparation:
    """
    Populates a spreedsheet file using Morninstar data.
    Made for fundamental analysis
    """

    path: str = "assets/base-sheet.xlsx"
    workbook: Workbook = None
    performanceIds: list
    symbols: list
    outputFilename: str = "comparation.xlsx"
    initialColumn: int = 3
    initialRow: int = 2
    rowMap: dict = {
        "currentRatio": 3,
        "quickRatio": 4,
        "debtToEquity": 6,
        "inventoryTurnover": 7,
        "daysInventory": 8,
        "AssetTurnover": 9,
        "roe": 10,
        "netMargin": 11,
        "PER": 12,
        "PCF": 13,
        "PS": 14,
        "PBV": 15,
        "price": 18,
        "PER-5yr": 26,
        "PCF-5yr": 29,
        "PS-5yr": 32,
        "PBV-5yr": 35,
    }

    def __init__(self):
        print("Loading...")
        self.workbook = load_workbook(filename=self.path)

    def do(self):
        sheet: Worksheet = self.workbook.active
        self._loadSymbolsAsHeaders(sheet)
        self._loadOverviewData(sheet)
        self._loadInstrumentsPrice(sheet)
        self._loadPastAvgValuation(sheet)
        self.workbook.save(filename=self.outputFilename)
        print("Finished")

    def _loadSymbolsAsHeaders(self, sheet: Worksheet):
        titleRow = 2
        for key, symbol in enumerate(self.symbols):
            sheet.cell(row=titleRow, column=self.initialColumn + key).value = symbol

    def _loadOverviewData(self, sheet: Worksheet):
        adapter = FallbackAdapter() if USE_FALLBACK_ADAPTER else OverviewAdapter()

        for key, perId in enumerate(self.performanceIds):
            symbol = self.symbols[key]
            try:
                data = adapter.fetch(perId)
            except AxlError as e:
                raise ComparatorError(phase="overview", symbol=symbol, original_error=e)

            sheet.cell(
                row=self.rowMap["currentRatio"], column=self.initialColumn + key
            ).value = data.currentRatio
            sheet.cell(
                row=self.rowMap["quickRatio"], column=self.initialColumn + key
            ).value = data.quickRatio
            sheet.cell(
                row=self.rowMap["debtToEquity"], column=self.initialColumn + key
            ).value = data.debtToEquity

            sheet.cell(
                row=self.rowMap["roe"], column=self.initialColumn + key
            ).value = data.roe
            sheet.cell(
                row=self.rowMap["netMargin"], column=self.initialColumn + key
            ).value = data.netMargin

            sheet.cell(
                row=self.rowMap["PER"], column=self.initialColumn + key
            ).value = data.per
            sheet.cell(
                row=self.rowMap["PCF"], column=self.initialColumn + key
            ).value = data.pcf
            sheet.cell(
                row=self.rowMap["PS"], column=self.initialColumn + key
            ).value = data.ps
            sheet.cell(
                row=self.rowMap["PBV"], column=self.initialColumn + key
            ).value = data.pbv

    def _loadInstrumentsPrice(self, sheet: Worksheet):
        try:
            response = getInstrumentsPrice(self.symbols)
        except AxlError as e:
            raise ComparatorError(phase="price", original_error=e)

        for key, data in enumerate(response):
            sheet.cell(
                row=self.rowMap["price"], column=self.initialColumn + key
            ).value = data["lastPrice"]

    def _loadPastAvgValuation(self, sheet: Worksheet):
        PS_index = 0
        PER_index = 1
        PCF_index = 2
        PBV_index = 3

        def getFiveYearValue(index, rows):
            pastData: list = rows[index]["datum"]
            penultimateIndex = len(pastData) - 2
            val = pastData[penultimateIndex]
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        for key, perId in enumerate(self.performanceIds):
            symbol = self.symbols[key]
            try:
                response = getAvgValuation(perId)
            except AxlError as e:
                raise ComparatorError(
                    phase="valuation", symbol=symbol, original_error=e
                )

            resp_rows = response["Collapsed"]["rows"]

            sheet.cell(
                row=self.rowMap["PER-5yr"], column=self.initialColumn + key
            ).value = getFiveYearValue(PER_index, resp_rows)
            sheet.cell(
                row=self.rowMap["PCF-5yr"], column=self.initialColumn + key
            ).value = getFiveYearValue(PCF_index, resp_rows)
            sheet.cell(
                row=self.rowMap["PS-5yr"], column=self.initialColumn + key
            ).value = getFiveYearValue(PS_index, resp_rows)
            sheet.cell(
                row=self.rowMap["PBV-5yr"], column=self.initialColumn + key
            ).value = getFiveYearValue(PBV_index, resp_rows)
