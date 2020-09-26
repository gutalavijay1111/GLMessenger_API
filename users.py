
# <-------------- Code added by Vijaykumar ---------->
# Please add this code to the zerver/lib/users.py
# <--------- start of code ----------->

# Function used by view backing the deactivate custom API.
# Access user by user_name
def access_user_by_user_name(user_profile: UserProfile, user_name: str,
                      allow_deactivated: bool=False, allow_bots: bool=False,
                      read_only: bool=False) -> UserProfile:
    try:
        target = get_user_profile_by_user_name_in_realm(user_name, user_profile.realm)
    except UserProfile.DoesNotExist:
        raise JsonableError(_("No such user"))
    if target.is_bot and not allow_bots:
        raise JsonableError(_("No such user"))
    if not target.is_active and not allow_deactivated:
        raise JsonableError(_("User is deactivated"))
    if read_only:
        # Administrative access is not required just to read a user.
        return target
    if not user_profile.can_admin_user(target):
        raise JsonableError(_("Insufficient permission"))
    return target

# <---------- end_of_code ----------->

# <-------------- Code By Vijaykumar Gutala ---------->
# Please add this code to the zerver/views/users.py
# <--------- start of code ----------->

#This is to create connection between users as TeamMate members.
def create_connection(request,user_profile: UserProfile) -> HttpResponse:
    connection_success_users_list = []
    inactive_user_list = []
    non_existing_user_list = []
    print(request.POST)
    connect = request.POST.get('connect')
    connect_to = request.POST.get('connect_to')

    # Check if UserProfile for connect exists.
    if len(connect_to) < 0:
        raise Exception("Atleast one user required to make connection")
    connect_to = connect_to.split(',')

    if UserProfile.objects.filter(email=connect).exists():
        target_user = UserProfile.objects.get(email=connect)

        # Check if TeamMate object of this user exists else create.
        if TeamMate.objects.filter(user=target_user).exists():
            team = TeamMate.objects.get(user=target_user)
            # Iterating over connect_to list.
            for user in connect_to:
                print("Connecting to >>>>>>>>>>>>>>",user)
                target, temp , is_inactive = connection_check(user)
                if is_inactive:
                    inactive_user_list.append(user)
                if target:
                    team.members.add(target)
                    team.save()
                    temp.members.add(target_user)
                    temp.save()
                    connection_success_users_list.append(temp.user.full_name)
                else:
                    if is_inactive == False:
                        non_existing_user_list.append(user)
                    else:
                        continue
                    # return json_error({'result':'error','msg':'No such user {}'.format(user)})
            if len(inactive_user_list) > 0:
                if len(connection_success_users_list) == 0:
                    if len(non_existing_user_list) > 0:
                        msg = 'Inactive users  {} and Non-existing users  {}'.format(inactive_user_list,non_existing_user_list)
                        return json_error({'msg':msg})
                    else:
                        msg = 'Inactive users  {}.'.format(inactive_user_list)
                        return json_error({'msg':msg})
                else:
                    msg = '{} connected with {} and Inactive users  {} and Non-existing users  {}.'.format(target_user.full_name,connection_success_users_list,inactive_user_list,non_existing_user_list)  
                    return json_success({'msg':msg})
            else:
                if len(non_existing_user_list)==1 and len(connection_success_users_list)==0:
                        msg = 'Non-existing user  {}.'.format(non_existing_user_list)  
                        return json_success({'msg':msg})    
                else:
                    msg = '{} connected with {} and  Non-existing users  {}.'.format(target_user.full_name,connection_success_users_list,non_existing_user_list)  
                    return json_success({'msg':msg})

        else:
            team = TeamMate.objects.create(user=target_user)
            team.save()
            for user in connect_to:
                target, temp , is_inactive = connection_check(user)
                # checking if user is inactive.
                if is_inactive:
                    inactive_user_list.append(user)
                if target:
                    team.members.add(target)
                    team.save()
                    temp.members.add(target_user)
                    temp.save()
                    connection_success_users_list.append(temp.user.full_name)
        if len(inactive_user_list) > 0:
            if len(connection_success_users_list) == 0:
                msg = 'Inactive users  {}.'.format(inactive_user_list)
            else:  
                msg = '{} connected with {} and Inactive users are {}.'.format(target_user.full_name,connection_success_users_list,inactive_user_list)
            return json_success({'result':'success','msg': msg })              
        else:
            msg = '{} and {} connected'.format(target_user.full_name,connection_success_users_list)
        return json_success({'result':'success','msg': msg })

    else:
        return json_error({'result':'error','msg':'The target user does not exist'})

# Function to run some basic checks before attempting connection.
def connection_check(user_name):
    if UserProfile.objects.filter(email=user_name).exists():
        checked_user = UserProfile.objects.get(email=user_name)
        if checked_user.is_active == False:
            return False, None, True

        if not TeamMate.objects.filter(user=checked_user).exists():           
            temp = TeamMate.objects.create(user=checked_user)
            temp.save()
            return checked_user, temp, False 
        else:
            temp = TeamMate.objects.get(user=checked_user)
            return checked_user, temp, False
    else:
        return False, None, False



def remove_connection(request: HttpRequest, user_profile: UserProfile) -> HttpResponse:
    disconnection_success_users_list = []
    non_existing_user_list = []
    inactive_user_list = []
    targeted_user = request.POST.get('targeted_user')
    disconnect_from = request.POST.get('disconnect_from')
    
    # Checking for target is empty
    if not targeted_user:
        json_error({'result':'error','msg':'This is a Required field'})

    # Checking for disconnect list  is empty
    if not disconnect_from:
        return json_error({'result':'error','msg':'No users to disconnect, please enter a valid user'})
    else:
        disconnect_from = disconnect_from.split(',')

    if UserProfile.objects.filter(email=targeted_user).exists():
        target_user = UserProfile.objects.get(email=targeted_user)

        if TeamMate.objects.filter(user=target_user).exists():
            team = TeamMate.objects.get(user=target_user)
            # Iterating over disconnect_from list.
            for user in disconnect_from:
                print("Disconnecting User : ",user)
                target, temp , is_inactive = connection_check(user)
                if is_inactive:
                    inactive_user_list.append(user)
                if target:
                    team.members.remove(target)
                    team.save()
                    temp.members.remove(target_user)
                    temp.save()
                    disconnection_success_users_list.append(temp.user.full_name)
                else:
                    if is_inactive == False:
                        non_existing_user_list.append(user)
                    else:
                        continue
                    # return json_error({'result':'error','msg':'No such user {}'.format(user)})
            if len(inactive_user_list) > 0:
                if len(disconnection_success_users_list) == 0:
                    if len(non_existing_user_list) > 0:
                        msg = 'Inactive users  {} and Non-existing users  {}'.format(inactive_user_list,non_existing_user_list)
                        return json_error({'msg':msg})
                    else:
                        msg = 'Inactive users  {}.'.format(inactive_user_list)
                        return json_error({'msg':msg})
                else:
                    msg = '{} disconnected from {} and Inactive users  {} and Non-existing users  {}.'.format(target_user.full_name,disconnection_success_users_list,inactive_user_list,non_existing_user_list)  
                    return json_success({'msg':msg})
            else:
                if len(non_existing_user_list)==1 and len(disconnection_success_users_list)==0:
                        msg = 'Non-existing user  {}.'.format(non_existing_user_list)  
                        return json_success({'msg':msg})    
                else:
                    msg = '{} disconnected from {} and  Non-existing users  {}.'.format(target_user.full_name,disconnection_success_users_list,non_existing_user_list)  
                    return json_success({'msg':msg})
    else:
        return json_error({'result':'error','msg':'No such targeted user.'})


def reactivate_by_user_name(request: HttpRequest,
                            user_profile: UserProfile,
                            user_name: str
                             ) -> HttpResponse:

    target = UserProfile.objects.filter(email=user_name).exists()
    
    # checking if such user exists
    if target:
        # checking if already an activated user or not
        target_user = UserProfile.objects.filter(email=user_name).first()
        if target_user.is_active == True:
            return json_error({'result':'error','msg':'Already an activated User.'})
        else:
            target_user = UserProfile.objects.filter(email=user_name).update(is_active=True)
            return json_success({'result':'success','msg':'User {} Reactivated.'.format(user_name)})
    else:
        return json_error({'result':'error','msg':'No such User'})


# importing do_create_user_func from actions.py 
from zerver.lib.actions import (
    do_create_user_func,
)
# View backing up the create/update use API
def create_user(
    request: HttpRequest,
    user_profile: UserProfile,
    files: IO[Any]=None,

) -> HttpResponse:

    # Checking if image uploaded.
    if request.FILES:
        files = list(request.FILES.values())[0]
        uploaded_image = files
    else:
        uploaded_image = False

    # Email is a required field, throw error if not entered.
    if not request.POST.get('email'):
        return json_error({'result': 'error','msg':'Email is a required field'})
    # fetching email from post data
    email = request.POST.get('email')
    try:
        email_allowed_for_realm(email, user_profile.realm)
    except DomainNotAllowedForRealmError:
        return json_error(_("Email '{email}' not allowed in this organization").format(
            email=email,
        ))
    except DisposableEmailError:
        return json_error(_("Disposable email addresses are not allowed in this organization"))
    except EmailContainsPlusError:
        return json_error(_("Email addresses containing + are not allowed."))
    # try:
    #     get_user_by_delivery_email(email, user_profile.realm)
    #     return json_error(_("Email '{}' already in use").format(email))
    # except UserProfile.DoesNotExist:
    #     pass

    if request.POST.get('password'):
        password = request.POST.get('password')
        if not check_password_strength(password):
            return json_error(PASSWORD_TOO_WEAK_ERROR)
        if UserProfile.objects.filter(delivery_email=email).exists():
            user = UserProfile.objects.get(delivery_email=email)
            if request.POST.get('full_name'):
                full_name_raw = request.POST.get('full_name')
                old_name = user.full_name
                user.full_name = full_name_raw
                user.save()
                if uploaded_image:
                    upload_avatar_image(uploaded_image, user_profile, user)
                    do_change_avatar_fields(user, UserProfile.AVATAR_FROM_USER, acting_user=user_profile)
                    user_avatar_url = avatar_url(user)
                    return json_success({'msg': 'Full_name for {} updated to {} , Avatar updated successfuly '.format(old_name,user.full_name)})
                return json_success({'msg': 'Full_name for {} updated to {} , updated successfuly '.format(old_name,user.full_name)})
            else:
                if uploaded_image:
                    upload_avatar_image(uploaded_image, user_profile, user)
                    do_change_avatar_fields(user, UserProfile.AVATAR_FROM_USER, acting_user=user_profile)
                    user_avatar_url = avatar_url(user)
                    return json_success({'msg': 'Avatar updated successfuly '.format()})
                else:
                    return json_success({'msg': 'No action can be performed'})
        else:
            if request.POST.get('full_name'):
                full_name = request.POST['full_name']
                form = CreateUserForm({'full_name': full_name, 'email': email})
                if not form.is_valid():
                    return json_error(_('Bad name or username'))
                realm = user_profile.realm
                target_user = do_create_user_func(email, password, realm, full_name, acting_user=user_profile)
            if uploaded_image:
                upload_avatar_image(uploaded_image, user_profile, target_user)
                do_change_avatar_fields(target_user, UserProfile.AVATAR_FROM_USER, acting_user=user_profile)
                user_avatar_url = avatar_url(target_user)
                return json_success({'user_id': target_user.id})
            return json_success({'user_id': target_user.id})

    else:
        if UserProfile.objects.filter(delivery_email=email).exists():
            user = UserProfile.objects.get(delivery_email=email)
            if request.POST.get('full_name'):
                full_name_raw = request.POST.get('full_name')
                old_name = user.full_name
                user.full_name = full_name_raw
                user.save()
                if uploaded_image:
                    upload_avatar_image(uploaded_image, user_profile, user)
                    do_change_avatar_fields(user, UserProfile.AVATAR_FROM_USER, acting_user=user_profile)
                    user_avatar_url = avatar_url(user)
                    return json_success({'msg': 'Full_name for {} updated to {} , Avatar updated successfuly '.format(user.full_name,old_name)})
                return json_success({'msg': 'Full_name for {} updated to {} , updated successfuly '.format(user.full_name,old_name)})        
            else:
                if uploaded_image:
                    upload_avatar_image(uploaded_image, user_profile, user)
                    do_change_avatar_fields(user, UserProfile.AVATAR_FROM_USER, acting_user=user_profile)
                    user_avatar_url = avatar_url(user)
                    return json_success({'msg': 'Avatar updated successfuly '.format()})
                else:
                    return json_success({'msg':'No action to perform'})

# importing access_user_by_user_name function from lib/users.py
from zerver.lib.users import (
    access_user_by_user_name,
)       

# View backing the deactivate_user_by_username custom API.
def deactivate_user_backend_by_user_name(request: HttpRequest, user_profile: UserProfile,
                            user_name: str) -> HttpResponse:
    target = access_user_by_user_name(user_profile, user_name)
    if target.is_realm_owner and not user_profile.is_realm_owner:
        raise OrganizationOwnerRequired()
    if check_last_owner(target):
        return json_error(_('Cannot deactivate the only organization owner'))
    return deactivate_user_profile(request, user_profile, target)

# importing deactivate_user function from actions.py
from zerver.lib.actions import (
    deactivate_user,
)
# this function deactivates the user_profile
def deactivate_user_profile(request: HttpRequest, user_profile: UserProfile,
                                     target: UserProfile) -> HttpResponse:
    deactivate_user(target, acting_user=user_profile)
    return json_success({'result':'success','msg':'User {} deactivated successfully by {}'.format(target.full_name,user_profile.full_name)})

# <---------- end_of_code ----------->