from django.core.management.base import BaseCommand, CommandError
import datetime
import decimal

from ...models import Credit,PocketMoney
from ...views import AccountHistorySerializer



class Command(BaseCommand):

    def handle(self, *args, **options):
        self.update_money_pocket_money()
        self.update_money_credit()

    def update_money_credit(self):
        credits = Credit.objects.all()
        month = datetime.date.today().month
        day = datetime.date.today().day
        for obj in credits:
            if obj.is_accepted:
                if obj.start_date == datetime.date.today():
                    data = {
                        "child": obj.child,
                        "date": datetime.datetime.now(),
                        "amount": obj.amount,
                        "description": "Pieniądze uzyskane z kredytu",
                        "money_after_transaction": obj.child.money + obj.amount
                    }
                    account = AccountHistorySerializer()
                    account.create(validated_data=data)
                    obj.child.money = obj.child.money + obj.amount
                    obj.child.save()
                    return
                if obj.end_date == datetime.date.today():
                    data = {
                        "child": obj.child,
                        "date": datetime.datetime.now(),
                        "amount": obj.installment_amount*decimal.Decimal(-1),
                        "description": "Ostatnia rata kredytu, kredyt zakończony",
                        "money_after_transaction": obj.child.money - obj.installment_amount
                    }
                    account = AccountHistorySerializer()
                    account.create(validated_data=data)
                    obj.child.money = obj.child.money - obj.installment_amount
                    obj.child.save()
                    obj.delete()
                    return
                if obj.start_date.day > 28 and month == 2 and day == 28:
                    data = {
                        "child": obj.child,
                        "date": datetime.datetime.now(),
                        "amount": obj.installment_amount * decimal.Decimal(-1),
                        "description": "Rata kredytu",
                        "money_after_transaction": obj.child.money - obj.installment_amount
                    }
                    account = AccountHistorySerializer()
                    account.create(validated_data=data)
                    obj.child.money = obj.child.money - obj.installment_amount
                    obj.child.save()
                    return
                if obj.start_date.day > 30 and (month == 4 or month == 6 or month == 9 or month == 11) and day == 30:
                    data = {
                        "child": obj.child,
                        "date": datetime.datetime.now(),
                        "amount": obj.installment_amount * decimal.Decimal(-1),
                        "description": "Rata kredytu",
                        "money_after_transaction": obj.child.money - obj.installment_amount
                    }
                    account = AccountHistorySerializer()
                    account.create(validated_data=data)
                    obj.child.money = obj.child.money - obj.installment_amount
                    obj.child.save()
                    return
                if obj.start_date.day == day:
                    data = {
                        "child": obj.child,
                        "date": datetime.datetime.now(),
                        "amount": obj.installment_amount * decimal.Decimal(-1),
                        "description": "Rata kredytu",
                        "money_after_transaction": obj.child.money - obj.installment_amount
                    }
                    account = AccountHistorySerializer()
                    account.create(validated_data=data)
                    obj.child.money = obj.child.money - obj.installment_amount
                    obj.child.save()
                    return

    def update_money_pocket_money(self):
        pocket_money = PocketMoney.objects.all()
        month = datetime.date.today().month
        day = datetime.date.today().day
        for obj in pocket_money:
            if obj.start_date.day > 28 and month == 2 and day == 28:
                data = {
                    "child": obj.child,
                    "date": datetime.datetime.now(),
                    "amount": obj.amount,
                    "description": "Kieszonkowe",
                    "money_after_transaction": obj.child.money + obj.amount
                }
                account = AccountHistorySerializer()
                account.create(validated_data=data)
                obj.child.money = obj.child.money + obj.amount
                obj.child.save()
                return
            if obj.start_date.day > 30 and (month == 4 or month == 6 or month == 9 or month == 11) and day == 30:
                data = {
                    "child": obj.child,
                    "date": datetime.datetime.now(),
                    "amount": obj.amount,
                    "description": "Kieszonkowe",
                    "money_after_transaction": obj.child.money + obj.amount
                }
                account = AccountHistorySerializer()
                account.create(validated_data=data)
                obj.child.money = obj.child.money + obj.amount
                obj.child.save()
                return
            if obj.start_date.day == day:
                data = {
                    "child": obj.child,
                    "date": datetime.datetime.now(),
                    "amount": obj.amount,
                    "description": "Kieszonkowe",
                    "money_after_transaction": obj.child.money + obj.amount
                }
                account = AccountHistorySerializer()
                account.create(validated_data=data)
                obj.child.money = obj.child.money + obj.amount
                obj.child.save()
                return
