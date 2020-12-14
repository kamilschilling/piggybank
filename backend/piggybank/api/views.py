from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from .serializers import *
from .models import *
from .permissions import *
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from django.db.models import Q
import datetime
import decimal



class ChangePasswordAPIView(APIView):

    def put(self,request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            password = serializer.data.get("password")
            if not request.user.check_password(password):
                return Response({"error":"Stare hasło jest błędne"},status=400)
            serializer.update(request.user,request.data)
            login(request, request.user)
            return Response(status=200)
        else:
            return Response({"error":"Dane są niepoprawne"},status=400)


@permission_classes([permissions.AllowAny,])
class RegisterAPIView(APIView):

    def post(self,request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.validate(request.data)
            serializer.create(request.data)
            return Response(status=201)
        return Response({"error":"Dane są niepoprawne"},status=400)





@permission_classes([permissions.AllowAny,])
class LoginAPIView(APIView):

    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid()
        try:
            request.user.auth_token.delete()
            logout(request)
        except: pass
        user = serializer.validate(request.data)
        login(request,user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, 'id': token.user.id}, status=200)


class LogoutAPIView(APIView):

    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response(status=204)


class ParentViewSet(viewsets.ModelViewSet):
    serializer_class = ParentSerializer
    queryset = Parent.objects.all()
    permission_classes = (WithoutPost,)


    def get_queryset(self):
        user = self.request.user
        try:
            return Parent.objects.filter(user=user)
        except:
            return Response({"error":"Nie możesz podglądać konta rodzica"},status=403)

    def update(self, request, *args, **kwargs):
        serializer = UpdateParentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            instance = self.get_object()
            instance.name = request.data.get("name")
            instance.save()
            return Response(status=200)
        else:
            return Response({"error":"Dane są niepoprawne"},status=400)


class ChildViewSet(viewsets.ModelViewSet):
    serializer_class = ChildSerializer
    queryset = Child.objects.all()

    def get_queryset(self):
        user = self.request.user
        try:
            return Child.objects
        except:
            return Child.objects.filter(user=user)

    def update(self, request, *args, **kwargs):
        try:
            request.user.parent.isParent
        except:
            return Response({"error":"Nie możesz zmieniać samemu swojego konta"},status=403)
        serializer = ChildSerializer(data=request.data)
        serializer.is_valid()
        serializer.validate(request.data)
        instance = self.get_object()
        old_money = float(instance.money)
        new_money = float(request.data.get('money'))
        if new_money!=0:
            if new_money > 0:
                desc = "Wpłata na konto"
            else:
                desc = "Wypłata z konta"
            data = {
                "child": instance,
                "date": datetime.datetime.now(),
                "amount": new_money,
                "description": desc,
                "money_after_transaction": old_money+new_money
            }
            account = AccountHistorySerializer()
            account.create(validated_data=data)
            instance.money = old_money+new_money
        instance.name = request.data.get('name')
        instance.save()

        return Response(status=200)

    def destroy(self, request, *args, **kwargs):
        try:
            request.user.parent.isParent
        except:
            return Response({"error":"Nie możesz samemu usunać swojego konta"},status=403)
        instance = self.get_object()
        self.perform_destroy(instance)
        self.perform_destroy(instance.user)
        return Response(status=204)

    def create(self, request, *args, **kwargs):
        try:
            request.user.parent.isParent
        except:
            return Response({"error":"Jako dziecko nie możesz mieć dzieci"},status=403)
        if request.data.get('parent') == str(request.user.parent.id):
            if Child.objects.filter(parent=request.user.parent).count()>14:
                return Response({"error":"Nie możesz dodać wiecej niż 15 dzieci"},status=403)
            super().create(request, *args, **kwargs)
            return Response(status=201)
        else:
            return Response({"error":"Nie możesz tworzyć konta dziecka dla kogoś innego"},status=400)

class CreditViewSet(viewsets.ModelViewSet):
    serializer_class = CreditSerializer
    queryset = Credit.objects.all()
    filterset_fields = ('is_accepted','child',)

    def is_parent(self):
        try:
            parent = self.request.user.child.isParent
        except:
            parent = True
        return parent


    def get_queryset(self):
        user = self.request.user
        if not self.is_parent():
            return Credit.objects.filter(child=user.child)
        else:
            children = Child.objects.filter(parent=user.parent)
            return Credit.objects.filter(child__in=children).order_by('id')

    def create(self, request, *args, **kwargs):
        if self.is_parent():
            child = Child.objects.filter(Q(parent=request.user.parent) & Q(id=request.data.get('child', None)))
        else:
            child = Child.objects.filter(Q(id=request.data.get('child', None)))
            if child[0].id != int(request.user.child.id):
                return Response({"error":"Wybrano złego użytkownika"},status=403)
        if not child:
            return Response({"error":"To nie Twoje dziecko"},status=403)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parent = self.is_parent()
        is_today = request.data.get('start_date') == str(datetime.date.today())
        if bool(request.data.get('is_accepted')) and is_today:
            if not parent:
                return Response({"error":"Nie możesz sam zaakceptować kredytu, musi to zrobic rodzic"},status=400)
            else:
                child[0].money += decimal.Decimal.from_float(float(request.data.get('amount')))
                child[0].save()
                data = {
                    "child": child[0],
                    "date": datetime.datetime.now(),
                    "amount": request.data.get('amount'),
                    "description": "Pieniądze uzyskane z kredytu",
                    "money_after_transaction": child[0].money+decimal.Decimal.from_float(float(request.data.get('amount')))
                }
                account = AccountHistorySerializer()
                account.create(validated_data=data)
        self.perform_create(serializer)
        return Response(status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = CreditUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance.start_date < datetime.date.today():
            return Response({"error":"Nie możesz akceptować ani zmieniać kredytu którego data startu już minęła,"
                                     " musisz usunać kredyt i stworzyć nowy"},status=403)
        if str(instance.start_date)!=request.data.get('start_date'):
            return Response({"error":"Nie możesz zmieniać daty startowej kredytu, wszystkie raty i "
                                     "obliczenia zostały wykonane dla pierwotnej daty startu kredytu,"
                                     "musisz usunać kredyt i stworzyć nowy"},status=403)
        if bool(request.data.get('is_accepted')) and not self.is_parent():
            return Response({"error":"Nie możesz sam zaakceptować kredytu, musi to zrobic rodzic"},status=403)
        if instance.is_accepted:
            return Response({"error":"Nie można edytować zatwierdzonego kredytu, możesz jedynie go usunać"},status=403)
        is_today = request.data.get('start_date') == str(datetime.date.today())
        if bool(request.data.get('is_accepted')) and not instance.is_accepted and is_today:
            child = Child.objects.filter(Q(id=request.data.get('child', None)))[0]
            child.money += decimal.Decimal.from_float(float(request.data.get('amount')))
            child.save()
            data = {
                "child": child,
                "date": datetime.datetime.now(),
                "amount": request.data.get('amount'),
                "description": "Pieniądze uzyskane z kredytu",
                "money_after_transaction": child.money+decimal.Decimal.from_float(float(request.data.get('amount')))
            }
            account = AccountHistorySerializer()
            account.create(validated_data=data)
        self.perform_update(serializer)
        return Response(status=200)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_accepted and not self.is_parent():
            return Response({"error":"Nie możesz usunąć zaakceptowanego kredytu, tylko rodzic może to zrobić"},status=403)
        self.perform_destroy(instance)
        return Response(status=204)



class AccountHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = AccountHistorySerializer
    queryset = AccountHistory.objects.all()
    permission_classes = (ReadOnly,)
    filterset_fields = ('child',)

    def get_queryset(self):
        user = self.request.user
        try:
            parent = user.child.isParent
        except:
            parent =True
        if not parent:
            return AccountHistory.objects.filter(child=user.child).order_by('-id')
        else:
            children = Child.objects
            return AccountHistory.objects


class PocketMoneyViewSet(viewsets.ModelViewSet):
    serializer_class = PocketMoneySerializer
    queryset = PocketMoney.objects.all()
    permission_classes = (ReadOnlyForChild,)


    def get_queryset(self):
        user = self.request.user
        try:
            parent = user.child.isParent
        except:
            parent = True
        if not parent:
            return PocketMoney.objects.filter(child=user.child)
        else:
            children = Child.objects.filter(parent=user.parent)
            return PocketMoney.objects.filter(child__in=children)

    def create(self, request, *args, **kwargs):
        child= Child.objects.filter(Q(parent=request.user.parent) & Q(id=request.data.get('child',None)))
        if child:
            super().create(request, *args, **kwargs)
            if request.data.get('start_date') == str(datetime.date.today()):
                old_money = child[0].money
                data = {
                    "child": child[0],
                    "date": datetime.datetime.now(),
                    "amount": request.data.get('amount'),
                    "description": "Kieszonkowe",
                    "money_after_transaction": old_money + decimal.Decimal.from_float(float(request.data.get('amount')))
                }
                account = AccountHistorySerializer()
                account.create(validated_data=data)
                child[0].money = old_money + decimal.Decimal.from_float(float(request.data.get('amount')))
                child[0].save()
            return Response(status=201)
        else:
            return Response({"error":"Nie możesz stworzyć kieszonkowego dla cudzego dziecka"},status=403)

    def update(self, request, *args, **kwargs):
        child= Child.objects.filter(Q(parent=request.user.parent) & Q(id=request.data.get('child',None)))
        if child:
            super().update(request, *args, **kwargs)
            if request.data.get('start_date') == str(datetime.date.today()):
                old_money = child[0].money
                data = {
                    "child": child[0],
                    "date": datetime.datetime.now(),
                    "amount": request.data.get('amount'),
                    "description": "Kieszonkowe",
                    "money_after_transaction": old_money + decimal.Decimal.from_float(float(request.data.get('amount')))
                }
                account = AccountHistorySerializer()
                account.create(validated_data=data)
                child[0].money = old_money + decimal.Decimal.from_float(float(request.data.get('amount')))
                child[0].save()
            return Response(status=200)
        else:
            return Response({"error":"Nie możesz edytować kieszonkowego obcego dziecka"},status=403)