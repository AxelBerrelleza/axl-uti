class MS:
    """
    From Morningstar API
    """
    OVERVIEW = {
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

    def instruments(count: int = 1):
        _INSTRUMENT = {
            'status': 'OK',
            'lastPrice': 116.56,
            'lastClose': 117.14,
            'tradingStatus': 'Closed',
            'marketCap': 53409182444.24,
            'yearRangeHigh': 181.86,
            'yearRangeLow': 112.53,
            'currencyCode': 'USD',
            'currencySymbol': '$',
            'listedCurrency': 'USD',
            'tradedCurrency': None,
            'exchangeID': 'XNYS',
            'exchangeName': 'New York Stock Exchange',
            'exchangeTimeZone': 'EST',
            'type': 'Equity',
            'dayChange': -0.58,
            'dayChangePer': -0.4951,
            'message': '126.1.TGT',
            'lastCloseAsOfDate': None
        }
        
        return [_INSTRUMENT for _ in range(0, count)]

    AVG_VALUATION = {
        'Collapsed': {
            'rows': [
                {'label': 'Price/Sales', 'salDataId': 'price.sales.label', 'datum': ['3.18', '2.8253', '3.5613', '3.392', '3.496', '4.7598', '3.7405', '1.7092', '2.8507', '3.779', '3.4249', '3.1258', '2.975'], 'subLevel': ''},
                {
                    'label': 'Price/Earnings',
                    'salDataId': 'price.earnings.label',
                    'datum': ['951.9577', '171.595', '297.5751', '84.0969', '81.8715', '95.2319', '65.213', '76.3984', '79.5497', '46.8782', '36.8535', '70.7129', '25.6805'],
                    'subLevel': ''
                },
                {
                    'label': 'Price/Cash Flow',
                    'salDataId': 'price.cash.flow.label',
                    'datum': ['94.0502', '107.0845', '263.6281', '19.1414', '23.7463', '33.3578', '25.3499', '14.0008', '18.3273', '19.2337', '16.6259', '21.2279', '17.9437'],
                    'subLevel': ''
                },
                {
                    'label': 'Price/Book',
                    'salDataId': 'price.book.label',
                    'datum': ['25.5022', '20.0308', '22.8601', '18.7722', '16.1867', '19.7521', '14.0217', '6.2305', '8.578', '8.8983', '7.5492', '10.4751', '4.4777'],
                    'subLevel': ''
                }
            ],
            'columnDefs': ['Calendar', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', 'Current', '5-Yr', 'Index'],
            'columnDefs_labels': [
                'tabular.data.label.column.year',
                '2015',
                '2016',
                '2017',
                '2018',
                '2019',
                '2020',
                '2021',
                '2022',
                '2023',
                '2024',
                'valuation.headers.current',
                'valuation.headers.fiveyear',
                'valuation.headers.index'
            ],
            'userType': None,
            'footer': {'asOfLabel': 'As of', 'asOfDate': '2025-03-04T00:00:00.000', 'indexLabel': 'Index:', 'indexName': 'Morningstar US Market TR USD', 'enterpriseValueCurrency': 'USD'}
        },
        'Expanded': {
            'rows': [
                {
                    'label': 'Price/Forward Earnings',
                    'salDataId': 'price.forward.earnings.label',
                    'datum': [None, '70.0813', '129.5094', '38.2278', '47.332', '45.2088', '30.2489', '41.3793', '39.4649', '27.2027', '31.0198', '51.0217', None],
                    'subLevel': ''
                },
                {'label': 'PEG Ratio', 'salDataId': 'peg.ratio.label', 'datum': ['8.8934', '9.4668', '2.5239', '0.649', '0.639', '0.8136', '1.0262', '1.8583', '4.844', '1.4246', '0.999', '2.1592', None], 'subLevel': ''},
                {'label': 'Earnings Yield %', 'salDataId': 'earnings.yield.label', 'datum': ['0.11', '0.58', '0.34', '1.19', '1.22', '1.05', '1.53', '1.31', '1.26', '2.13', '2.71', '1.13', None], 'subLevel': ''},
                {
                    'label': 'Enterprise Value (Bil)',
                    'salDataId': 'enterprise.value.label',
                    'datum': ['310.65', '346.17', '563.94', '729.34', '932.28', '1647.28', '1725.92', '926.53', '1642.97', '2353.53', '2189.52', '1119.42', None],
                    'subLevel': '',
                    'orderOfMagnitude': 'Bil'
                },
                {
                    'label': 'Enterprise Value/EBIT',
                    'salDataId': 'enterprise.value.ebit.label',
                    'datum': ['216.9319', '85.5589', '157.6118', '67.5623', '66.4303', '76.6607', '53.4456', '80.8983', '69.6795', '40.4595', '33.003', '60.2871', None],
                    'subLevel': ''
                },
                {
                    'label': 'Enterprise Value/EBITDA',
                    'salDataId': 'enterprise.value.ebitda.label',
                    'datum': ['42.3167', '29.7987', '40.7026', '28.7457', '27.4888', '36.3711', '26.7979', '18.5191', '22.9571', '21.5615', '18.378', '25.1174', None],
                    'subLevel': ''
                }
            ],
            'columnDefs': ['Calendar', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', 'Current', '5-Yr', 'Index'],
            'columnDefs_labels': [
                'tabular.data.label.column.year',
                '2015',
                '2016',
                '2017',
                '2018',
                '2019',
                '2020',
                '2021',
                '2022',
                '2023',
                '2024',
                'valuation.headers.current',
                'valuation.headers.fiveyear',
                'valuation.headers.index'
            ]
        }
    }