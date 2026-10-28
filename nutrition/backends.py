

from django.contrib.auth.backends import BaseBackend

from nutrition.models import User

class EmailBackEnd(BaseBackend):

    def authenticate(self, request, username = None, password = None, **kwargs):

        try:

            user_object = User.objects.get(email=username)

            # if user_object.password == password:

            if user_object.check_password(password):

                return user_object
            
            else:

                return None
            
        except Exception as e:

            return None
        
    def get_user(self, user_id):

        try:

            return User.objects.get(id=user_id)
        
        except Exception as e:

            return None
        
class PhoneNumberBackEnd(BaseBackend):

    def authenticate(self, request, username = None, password = None, **kwargs):

        try:

            user_object = User.objects.get(phone=username)

            if user_object.check_password(password):

                return user_object
            
            else:

                return None
            
        except Exception as e:

            return None
        
    def get_user(self, user_id):
        
        try:

            User.objects.get(id= user_id)

        except Exception as e:

            return None


        


        
