import decimal
import datetime


def correction_installment_and_end_date(amount,inst_amount,start_date):
    cycle = (amount / inst_amount)
    cycle = cycle.__ceil__()
    over = (cycle * inst_amount) - amount
    correction = over / cycle
    inst_amount = inst_amount - correction
    inst_amount = inst_amount * decimal.Decimal(100)
    inst_amount = inst_amount.__ceil__()
    inst_amount = inst_amount / decimal.Decimal(100)
    years = (cycle/decimal.Decimal(12)).__floor__().__int__()
    cycle = cycle.__int__()
    months = cycle - (years*12)
    month = start_date.month + months
    if month >12:
        month-=12
        years+=1
    end_date = datetime.date(start_date.year + years, month, start_date.day)
    data = {
        "inst_amount": inst_amount,
        "end_date": end_date
    }
    return data
