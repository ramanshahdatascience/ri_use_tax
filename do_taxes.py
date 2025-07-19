#! /usr/bin/env python3


from datetime import date
from sys import argv

import openpyxl
import pandas as pd


TAX_RATE = 0.07
ANNUAL_INTEREST = 0.12  # Accrue simple interest month by month on overdue tax
PENALTY = 0.1  # One-time penalty on overdue tax, not subject to interest
DAY_OF_MONTH_TAX_DUE = 20

# Access out of state purchases as a Pandas DataFrame
wb = openpyxl.load_workbook(filename=argv[1], data_only=True)
ws_data = wb['out_of_state_purchases'].values
header = next(ws_data)
raw_transactions = pd.DataFrame([r for r in ws_data], columns=header)

# Transactions relevant for an upcoming filing have all transaction data
# (vendor name and address, purchase date, qty and description, tax paid) but
# no tax remitted date.
transactions = \
    raw_transactions[~raw_transactions['vendor_name_and_address'].isnull()]\
                    [~raw_transactions['purchase_date'].isnull()]\
                    [~raw_transactions['qty_and_description_of_property_purchased'].isnull()]\
                    [~raw_transactions['total_sale_price'].isnull()]\
                    [~raw_transactions['tax_paid'].isnull()]\
                    [raw_transactions['tax_remitted_date'].isnull()]

# Compute
transactions['amt_of_tax'] = TAX_RATE * transactions['total_sale_price']
transactions['credit'] = transactions['tax_paid']

# Use a simple encoding (index = 12 * Gregorian year + month index) to do month
# arithmetic to compute months late
filing_date = date.fromisoformat(argv[2])
if filing_date.day <= DAY_OF_MONTH_TAX_DUE:
    filing_month = filing_date.year * 12 + filing_date.month - 1
else:
    filing_month = filing_date.year * 12 + filing_date.month

transactions['months_late'] = filing_month - \
    (transactions['purchase_date'].dt.year * 12 + \
     transactions['purchase_date'].dt.month)
transactions.loc[transactions['months_late'] < 0, 'months_late'] = 0

transactions['interest'] = ANNUAL_INTEREST * \
    transactions['months_late'] / 12 * \
    transactions['amt_of_tax']

transactions['penalty'] = PENALTY * \
    (transactions['months_late'] > 0) * \
    transactions['amt_of_tax']

filing_total_sale_price = transactions['total_sale_price'].sum()
filing_total_amt_of_tax = transactions['amt_of_tax'].sum()
filing_total_credit = transactions['credit'].sum()
filing_total_interest = transactions['interest'].sum()
filing_total_penalty = transactions['penalty'].sum()

# Output results as CSV but with footer for totals
with open(argv[3], 'w', newline='') as cf:
    cf.write(transactions[['vendor_name_and_address',
                           'purchase_date',
                           'qty_and_description_of_property_purchased',
                           'total_sale_price',
                           'amt_of_tax',
                           'credit',
                           'months_late',
                           'interest',
                           'penalty']]\
                .to_csv(header=True, index=False, float_format='%.2f'))

    cf.write('\n')
    cf.write('Totals,,,{:.2f},{:.2f},{:.2f},,{:.2f},{:.2f}'\
        .format(filing_total_sale_price,
                filing_total_amt_of_tax,
                filing_total_credit,
                filing_total_interest,
                filing_total_penalty))

    cf.write('\n\n')
    cf.write('Grand total (tax - credits + interest + penalty),{:.2f},,,,,,,'\
        .format(filing_total_amt_of_tax -
                filing_total_credit +
                filing_total_interest +
                filing_total_penalty))
    cf.write('\n')
