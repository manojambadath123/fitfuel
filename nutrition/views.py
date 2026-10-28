from django.shortcuts import render

# Create your views here.

from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView,DestroyAPIView,ListAPIView

from nutrition.serializers import UserSerializer,ProfileSerializer,FoodLogSerializer

from rest_framework import authentication,permissions

from rest_framework.views import APIView

from rest_framework.response import Response

from nutrition.models import User,Profile,FoodLog

from nutrition.permissions import Isowner,HasProfile

from nutrition.utility import analyze_food,generate_kerala_diet_plan


class UserCreateView(CreateAPIView):

    serializer_class = UserSerializer

class ProfileCreateView(CreateAPIView):

    serializer_class = ProfileSerializer

    authentication_classes = [authentication.TokenAuthentication]

    permission_classes = [permissions.IsAuthenticated]


    def perform_create(self, serializer):
        
        serializer.save(user= self.request.user)

class ProfileDetailView(RetrieveAPIView,UpdateAPIView):

    serializer_class = ProfileSerializer

    authentication_classes = [authentication.TokenAuthentication]

    permission_classes = [permissions.IsAuthenticated,HasProfile]

    def get_object(self):

        return self.request.user.profile

    # def get(self,request,*args,**kwargs):

    #     # instance = Profile.objects.get(user=request.user)

    #     profile_object = request.user.profile

    #     serializer_instance = ProfileSerializer(profile_object,many=False)

    #     return Response(data = serializer_instance.data)

from django.utils import timezone
from django.utils.dateparse import parse_date # str to datetime object conversion
from datetime import timedelta

class FoodLogListCreateView(CreateAPIView,ListAPIView):

    serializer_class = FoodLogSerializer


    authentication_classes = [authentication.TokenAuthentication]

    permission_classes = [permissions.IsAuthenticated,HasProfile]

    def perform_create(self, serializer):
        
        serializer.save(user=self.request.user)

    # def get_queryset(self):

    #     current_date = timezone.now().date()
        
    #     qs =  self.request.user.food_logs.filter(created_at__date=current_date)

    #     params = self.request.query_params #params = {"start_date:14","end_date":65"}

    #     if "start_date" in params and "end_date" in params:

    #         start_date = parse_date(params.get("start_date"))
    #         end_date = parse_date(params.get("end_date"))

    #         qs = self.request.user.food_logs.filter(created_at__date__gte=start_date,created_at__date__lte=end_date)

    #     if "filter_type" in params:

    #         filter_type = params.get("filter_type")

    #         if filter_type == "yesterday":

    #             yesterday = current_date - timedelta(days=1)

    #             print(yesterday)

    #             qs = self.request.user.food_logs.filter(created_at__date=yesterday)

    #         if filter_type == "this_week":

    #             this_week = current_date - timedelta(days=7)

    #             qs = self.request.user.food_logs.filter(created_at__date__gte=this_week)

    #     return qs
    

    
        # return self.request.user.food_logs.all()

    def get(self,request,*args,**kwargs):

        qs = request.user.food_logs.all()

        serializer_instance = FoodLogSerializer(qs,many=True)

        return Response(data = serializer_instance.data)
    

class FoodLogRetrieveUpdateDeleteView(RetrieveAPIView,UpdateAPIView,DestroyAPIView):

    serializer_class = FoodLogSerializer

    queryset = FoodLog.objects.all()

    authentication_classes = [authentication.TokenAuthentication]

    permission_classes = [Isowner,HasProfile]



class FoodScanView(APIView):

    authentication_classes = [authentication.TokenAuthentication]

    permission_classes = [permissions.IsAuthenticated,HasProfile]

    def post(self,request,*args,**kwargs):

        form_data = request.data

        image = form_data.get("image")

        try:

            data = analyze_food(image)

            qs =  FoodLog.objects.create(
                title=data.get("food_name"),
                calories=data.get("average_calorie"),
                meal_type=data.get("meal_type","breakfast"),
                user=request.user
            )

            serializer_instance = FoodLogSerializer(qs)

            return Response(data=serializer_instance.data)

        except Exception as e:

            print(e)
            
            return Response(data={"message":"food scanning failed..."})


class DietPlanView(APIView):

    authentication_classes = [authentication.TokenAuthentication]

    permission_classes = [permissions.IsAuthenticated,HasProfile]

    def post(self,request,*args,**kwargs):

        user_profile = request.user.profile

        goal = request.data.get("goal")

        target_weight = request.data.get("target_weight")

        duration = request.data.get("duration")

        age = user_profile.age

        weight = user_profile.weight

        gender = user_profile.gender

        try:

             data =  generate_kerala_diet_plan(goal=goal,age=age,weight=weight,gender=gender,target_weight=target_weight,duration=duration)

             return Response(data=data)
        
        except Exception as e:

            print(e)

            return Response(data={"message":"failed"})


from django.db.models import Sum
class SummaryView(APIView):

    authentication_classes = [authentication.TokenAuthentication]

    permission_classes = [permissions.IsAuthenticated,HasProfile]

    def get(self,request,*args,**kwargs):


        current_date = timezone.now().date()
        
        qs =  request.user.food_logs.filter(created_at__date=current_date)

        daily_calorie_target = request.user.profile.daily_calorie_goal

        params = request.query_params #params = {"start_date:14","end_date":65"}

        if "filter_type" in params:

            filter_type = params.get("filter_type")

            if filter_type == "yesterday":

                yesterday = current_date - timedelta(days=1)

                qs = request.user.food_logs.filter(created_at__date=yesterday)
        
            if filter_type == "this_week":

                this_week = current_date - timedelta(days=7)

                qs = request.user.food_logs.filter(created_at__date__gte=this_week)

                daily_calorie_target = daily_calorie_target*7


        total_consumed_calories = qs.values("calories").aggregate(total=Sum("calories"))["total"] or 0

        meal_type_summary = qs.values("meal_type").annotate(total=Sum("calories"))

        remaining = daily_calorie_target - total_consumed_calories

        context = {
                "daily_target":daily_calorie_target,
                "total_consumed":total_consumed_calories,
                "remaining":remaining,
                "meal_type_summary":meal_type_summary

            }
        
        return Response(data=context)


        # if len(qs)!=0:

        #     total_consumed_calories = qs.values("calories").aggregate(total=Sum("calories")).get("total",0)

        #     remaining = daily_calorie_target - total_consumed_calories

        #     context = {
        #         "daily_target":daily_calorie_target,
        #         "total_consumed":total_consumed_calories,
        #         "remaining":remaining
        #     }


        # else:

        #      context = {
        #         "daily_target":daily_calorie_target,
        #         "total_consumed":0,
        #         "remaining":daily_calorie_target
        #     }

    
        # return Response(data = context)




        

        # print("dailycalories=",daily_calorie)


        # print("consumedcalories=",consumed_calories)

        # consumed_cal = consumed_calories.get("total")

        

        # print("balancecalories=",balance)

        # return Response(data={"message":"calories"})

    