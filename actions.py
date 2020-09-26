
# <-------------- Code added by Vijaykumar ---------->
# <--------- start of code ----------->

# This is the function called by the View backing up create/update user custom API.
def do_create_user_func(email: str, password: Optional[str], realm: Realm, full_name: str,
                   bot_type: Optional[int]=None, role: Optional[int]=None,
                   bot_owner: Optional[UserProfile]=None, tos_version: Optional[str]=None,
                   timezone: str="", avatar_source: str=UserProfile.AVATAR_FROM_GRAVATAR,
                   default_sending_stream: Optional[Stream]=None,
                   default_events_register_stream: Optional[Stream]=None,
                   default_all_public_streams: Optional[bool]=None,
                   prereg_user: Optional[PreregistrationUser]=None,
                   newsletter_data: Optional[Dict[str, str]]=None,
                   default_stream_groups: Sequence[DefaultStreamGroup]=[],
                   source_profile: Optional[UserProfile]=None,
                   realm_creation: bool=False,
                   acting_user: Optional[UserProfile]=None) -> UserProfile:

    user_profile = create_user(email=email, password=password, realm=realm,
                               full_name=full_name,
                               role=role, bot_type=bot_type, bot_owner=bot_owner,
                               tos_version=tos_version, timezone=timezone, avatar_source=avatar_source,
                               default_sending_stream=default_sending_stream,
                               default_events_register_stream=default_events_register_stream,
                               default_all_public_streams=default_all_public_streams,
                               source_profile=source_profile)

    # Check if team for acting_user exists or not
    if TeamMate.objects.filter(user=acting_user).exists():
        # Team for acting_user Exists, just add user_profile
        team = TeamMate.objects.get(user=acting_user)
        team.members.add(user_profile)
        user_reverse = UserProfile.objects.get(id=acting_user.id)
        team_reverse = TeamMate.objects.create(user=user_profile)
        team_reverse.members.add(user_reverse)
        team_reverse.save()
    else:
        # first creating team of acting_user
        #adding user_profile to team of acting_user
        team = TeamMate.objects.create(user=acting_user)
        team.save(commit=False)
        team.members.add(user_profile)
        team.save()
        # adding acting_user to team of user_profile
        user_reverse = UserProfile.objects.get(id=acting_user.id)
        team_reverse = TeamMate.objects.create(user=user_profile)
        team_reverse.members.add(user_reverse)
        team_reverse.save()

    event_time = user_profile.date_joined
    if not acting_user:
        acting_user = user_profile
    RealmAuditLog.objects.create(
        realm=user_profile.realm, acting_user=acting_user, modified_user=user_profile,
        event_type=RealmAuditLog.USER_CREATED, event_time=event_time,
        extra_data=ujson.dumps({
            RealmAuditLog.ROLE_COUNT: realm_user_count_by_role(user_profile.realm),
        }))
    do_increment_logging_stat(user_profile.realm, COUNT_STATS['active_users_log:is_bot:day'],
                              user_profile.is_bot, event_time)
    if settings.BILLING_ENABLED:
        update_license_ledger_if_needed(user_profile.realm, event_time)

    # Note that for bots, the caller will send an additional event
    # with bot-specific info like services.
    notify_created_user(user_profile)
    if bot_type is None:
        process_new_human_user(user_profile, prereg_user=prereg_user,
                               newsletter_data=newsletter_data,
                               default_stream_groups=default_stream_groups,
                               realm_creation=realm_creation)
    return user_profile 


# This function deactivates the user_profie.
def deactivate_user(user_profile: UserProfile,
                       acting_user: Optional[UserProfile]=None,
                       _cascade: bool=True) -> None:
    team = TeamMate.objects.filter(user=user_profile).first()
    team.delete()
    
    if not user_profile.is_active:
        return

    if user_profile.realm.is_zephyr_mirror_realm:  # nocoverage
        # For zephyr mirror users, we need to make them a mirror dummy
        # again; otherwise, other users won't get the correct behavior
        # when trying to send messages to this person inside Zulip.
        #
        # Ideally, we need to also ensure their zephyr mirroring bot
        # isn't running, but that's a separate issue.
        user_profile.is_mirror_dummy = True
    user_profile.is_active = False
    user_profile.save(update_fields=["is_active"])

    delete_user_sessions(user_profile)
    clear_scheduled_emails([user_profile.id])

    event_time = timezone_now()
    RealmAuditLog.objects.create(
        realm=user_profile.realm, modified_user=user_profile, acting_user=acting_user,
        event_type=RealmAuditLog.USER_DEACTIVATED, event_time=event_time,
        extra_data=ujson.dumps({
            RealmAuditLog.ROLE_COUNT: realm_user_count_by_role(user_profile.realm),
        }))
    do_increment_logging_stat(user_profile.realm, COUNT_STATS['active_users_log:is_bot:day'],
                              user_profile.is_bot, event_time, increment=-1)
    if settings.BILLING_ENABLED:
        update_license_ledger_if_needed(user_profile.realm, event_time)

    event = dict(type="realm_user", op="remove",
                 person=dict(user_id=user_profile.id,
                             full_name=user_profile.full_name))
    send_event(user_profile.realm, event, active_user_ids(user_profile.realm_id))

    if user_profile.is_bot:
        event = dict(type="realm_bot", op="remove",
                     bot=dict(user_id=user_profile.id,
                              full_name=user_profile.full_name))
        send_event(user_profile.realm, event, bot_owner_user_ids(user_profile))

    if _cascade:
        bot_profiles = UserProfile.objects.filter(is_bot=True, is_active=True,
                                                  bot_owner=user_profile)
        for profile in bot_profiles:
            do_deactivate_user(profile, acting_user=acting_user, _cascade=False)

#<------------- end of code -------------->