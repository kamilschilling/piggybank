from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Child,Parent,Credit,AccountHistory,PocketMoney
from django.contrib.auth.models import User
from rest_framework.serializers import ValidationError
from .other import correction_installment_and_end_date
import datetime
import decimal


class ChangePasswordSerializer(serializers.ModelSerializer):

    new_password = serializers.CharField()
    new_password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ('password','new_password','new_password2')

    def validate(self, data):
        new_password= data.get('new_password',None)
        new_password2= data.get('new_password2',None)
        password = data.get('password',None)
        if len(new_password2) <5:
            raise  ValidationError('Hasło musi miec co najmniej 5 znakow')
        if new_password != new_password2:
            raise ValidationError('Nowe hasla nie sa takie same')
        if password == new_password:
            raise ValidationError('Nowe haslo nie moze byc takie jak stare haslo')
        return data

    def update(self, instance, validated_data):

        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password',)

    def validate(self, data):

        username = data.get('username', None)
        password = data.get('password', None)
        if username is None:
            raise ValidationError('Nie podales swojego nicku')

        if password is None:
            raise ValidationError('Nie podales hasla')

        user = authenticate(username=username,password=password)

        if user is None:
            raise ValidationError('Bledne dane logowania')

        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model= User
        fields=('username','password','email','id',)
        extra_kwargs = {'password': {'write_only': True},
                        'email': {'write_only': True},
                        'username': {'write_only': True}}



class RegisterSerializer(serializers.ModelSerializer):

    user = UserSerializer(required=True)
    password2=serializers.CharField()

    class Meta:
        model=Parent
        fields=('user','name','password2',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        parent, created = Parent.objects.update_or_create(user=user,name=validated_data.pop('name'))
        return parent

    def validate(self, data):
        name = data.get('name', None)
        password2= data.get('password2',None)
        user = data.get('user',None)
        if user['password'] != password2:
            raise ValidationError('Hasla nie sa takie same')
        if len(password2) <5:
            raise  ValidationError('Hasło musi miec co najmniej 5 znakow')
        if name is None:
            raise ValidationError('Nie podales imienia')
        if name is None:
            raise ValidationError('Nie podales kwoty')
        if len(name) > 30:
            raise ValidationError('Za dlugie imie')
        if len(name) < 3:
            raise ValidationError('Za krotkie imie')

        return data

class ParentSerializer(serializers.ModelSerializer):

    user = UserSerializer(required=True)

    class Meta:
        model=Parent
        fields=('user','name','id','isParent')

class UpdateParentSerializer(serializers.ModelSerializer):

    class Meta:
        model=Parent
        fields=('name',)


class ChildSerializer(serializers.ModelSerializer):

    user = UserSerializer(required=True)

    class Meta:
        model=Child
        fields = ('user', 'name', 'money', 'parent','id','isParent')

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        user = User.objects.create_user(**user_data)
        child, created = Child.objects.update_or_create(user=user,name=validated_data.pop('name'),
                                                        money=validated_data.pop('money'),
                                                        parent=validated_data.pop('parent'))
        return child

    def validate(self, data):
        name = data.get('name', None)
        money = data.get('money', None)
        if name is None:
            raise ValidationError('Nie podales imienia')
        if len(name) > 30:
            raise ValidationError('Za dlugie imie')
        if len(name) < 3:
            raise ValidationError('Za krotkie imie')
        if money is None:
            raise ValidationError('Stan poczatkowy konta musi byc podany')
        if name.isalpha() is False:
            raise ValidationError('Imie nie moze zawierac liczb i dziwnych znakow')
        return data


class CreditUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Credit
        fields = ('is_accepted',)


class CreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credit
        fields = '__all__'

    def validate(self, data):
        start_date = data.get('start_date',None)
        amount = data.get('amount',None)
        install_amount = data.get('installment_amount',None)

        if start_date < datetime.date.today():
            raise ValidationError('Kredyt nie moze sie zaczynac w przeszlosci')
        if amount <= decimal.Decimal(0):
            raise ValidationError('Kwota kredytu nie moze byc ujemna lub rowna 0')
        if install_amount <= decimal.Decimal(0):
            raise ValidationError('Kwota raty nie moze byc ujemna lub rowna 0')
        today = datetime.date.today()
        try:
            date_plus_month=today.replace(month=today.month + 1)
        except:
            date_plus_month=today.replace(year=today.year+1,month=1)
        if start_date > date_plus_month:
            raise ValidationError('Data startowa kredytu nie moze byc później niż miesiąc od dnia dzisiejszego')
        return data

    def create(self, validated_data):

        child = validated_data.pop('child')
        amount = validated_data.pop('amount')
        desc = validated_data.pop('description')
        is_accepted = validated_data.pop('is_accepted')
        start_date = validated_data.pop('start_date')
        inst_amount = validated_data.pop('installment_amount')

        data = correction_installment_and_end_date(amount,inst_amount,start_date)
        inst_amount = data['inst_amount']
        end_date = data['end_date']

        credit, created = Credit.objects.update_or_create(child=child,amount=amount,description=desc,
                                                          is_accepted=is_accepted,installment_amount=inst_amount,
                                                          start_date=start_date,end_date=end_date)
        return credit


class AccountHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountHistory
        fields = '__all__'


class PocketMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = PocketMoney
        fields = '__all__'

