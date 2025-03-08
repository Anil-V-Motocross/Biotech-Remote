from account.models import Address

def validate_user_profile(user):
    if user.is_active and user.first_name and user.last_name and user.date_of_birth and user.gender and user.mobile:
        # if user email is having mobile number appended with @@example.com then return false (split email bases on @ and check mobile number)
        if user.email.split('@')[0] == user.mobile:
            return {"user_profile": False, "message": "User profile is not updated. Update Email", "profile_status": False, "address_status":False}
        
        # user must have at leaest one address in address model
        if not Address.objects.filter(user=user).exists():
            return {"user_profile": False, "message": "User address is not updated.","profile_status": True, "address_status":False}
         
        return {"user_profile": True, "message": "User profile is valid.", "profile_status": True, "address_status": True}
    return {"user_profile": False, "message": "User profile is not updated.", "profile_status": False, "address_status":False}