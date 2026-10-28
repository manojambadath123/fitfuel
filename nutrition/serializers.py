

from rest_framework import serializers

from nutrition.models import User,Profile,FoodLog

class UserSerializer(serializers.ModelSerializer):

    password1 = serializers.CharField(write_only=True)

    password2 = serializers.CharField(write_only=True)

    class Meta:

        model = User

        fields = ["username","email","password","phone","password1","password2"]

        read_only_fields = ["password"]

    def create(self, validated_data):

        password1 = validated_data.pop("password1")
        password2 = validated_data.pop("password2")

        if password1!=password2:

            raise serializers.ValidationError("password mismatch!")

        return User.objects.create_user(**validated_data,password=password2)
    
class ProfileSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField(read_only=True)

    class Meta:

        model = Profile

        fields = "__all__"

        read_only_fields = ["id","user","bmi","daily_calorie_goal","created_at","updated_at"]

    def validate(self, data):

        age = data.get("age",12)

        if age not in range(12,101):

            raise serializers.ValidationError("invalid age")
        
        return data
        

class FoodLogSerializer(serializers.ModelSerializer):

    class Meta:

        model = FoodLog

        fields = "__all__"

        read_only_fields = ["id","user","created_at","updated_at"]

    def validate(self, data):
        
        calories = data.get("calories",0)

        if calories > 400:

            raise serializers.ValidationError("calories should be < 400")
        
        return data 