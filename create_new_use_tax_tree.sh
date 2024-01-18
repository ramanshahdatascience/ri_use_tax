#! /bin/bash

# Create a new year's directory tree with empty templates for use tax data
# Usage: ./create_new_use_tax_tree.sh ~/b/r/taxes/20xx_tax/ 20xx
mkdir ${1}/use_tax
mkdir ${1}/use_tax/business
cp use_tax_data_template.xlsx ${1}/use_tax/business/${2}-business-use-tax-data.xlsx

mkdir ${1}/use_tax/personal
cp use_tax_data_template.xlsx ${1}/use_tax/personal/${2}-personal-use-tax-data.xlsx
