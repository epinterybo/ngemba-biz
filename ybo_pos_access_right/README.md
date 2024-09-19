# POS Access Right Module for Odoo

## Overview
The **POS Access Right** module allows you to manage and restrict access to specific features in the Point of Sale (POS) system based on employee roles. This ensures that only authorized personnel can perform certain actions within the POS system.

## Installation

### Install Dependencies
Ensure the following Odoo modules are installed:
- Employees (`hr`)
- Point of Sale (`point_of_sale`)
- Discuss (`mail`)
- Inventory (`stock`)
- Invoicing (`account`)

### Download and Install
1. Download the module from the Odoo App Store.
2. Install it via the Odoo interface:
   - Navigate to `Apps`.
   - Search for `pos_access_right_hr`.
   - Click `Install`.

## Configuration

### Enable Multi-Employees per Session
1. Navigate to the POS settings (**Ensure you have no pos Open**).
2. Enable the option "Multi Employees per Session."

### Set Access Rights
1. Go to `Employees > Employees` and select an employee.
2. Under the POS tab, configure the access rights by enabling or disabling specific POS features for the selected employee.

## Usage

### Restrict POS Features
Admins can restrict the following buttons on the POS screen:
- Payment
- Customer
- Plus-Minus and Numpad
- Discount, Quantity, Price, and Remove

### Daily Operations
- Employees will see a customized POS interface based on their access rights.
- Only authorized employees will have access to restricted features.
