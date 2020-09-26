
# <-------------- Code added by Vijaykumar ---------->
# <--------- start of code ----------->
# <-------------- Custom API's ------------------->
    # Custom API end-point for making connections
    path('connect', rest_dispatch,
         {'POST': 'zerver.views.users.create_connection'}),

    # Custom API end-point for removing connections
    path('disconnect', rest_dispatch,
         {'POST': 'zerver.views.users.remove_connection'}),

    # Custom API end-point to create/update user       
    path('new_user', rest_dispatch,
         {'POST': 'zerver.views.users.create_user'}),

    # Custom API end-point to deactivate/terminate user by user_name
    path('users/deactivate/<str:user_name>', rest_dispatch,
         {'DELETE': 'zerver.views.users.deactivate_user_backend_by_user_name'}),

    # Cusstom API end-point to reactivate user by user_name
    path('users/reactivate/<str:user_name>', rest_dispatch,
         {'GET': 'zerver.views.users.reactivate_by_user_name'}),

# <----------- end of code ------------->