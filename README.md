## These are Custom API's for GL Messenger.

### You will need to update 4 files in your existing code_base to add these custom URLs
### 1. urls.py
>   **path:**  deployements/2020-08-24-08-50-53/zproject/urls.py
  - The name of the file 2020-08-24-08-50-53 will be different in your case.
  - Copy the code from urls.py from this repository and paste it within urls.py of your code_base.
  - Paste it within **v1_api_and_json_patterns**, you will find these at the begining of the code right below after all the imports. 
  
  ---
### 2. users.py (view)
>   **path:**  deployements/2020-08-24-08-50-53/zerver/views/users.py
  - The name of the file 2020-08-24-08-50-53 will be different in your case.
  - This file is a View file for our users API.
  - Copy the code from users.py from this repository and paste it within users.py of your code_base.
  - Paste it at the bottom
  
  ---
### 3. users.py (library)
>   **path:**  deployements/2020-08-24-08-50-53/zerver/lib/users.py
  - The name of the file 2020-08-24-08-50-53 will be different in your case.
  - This users.py is a Core file and not a View.
  - Copy the code from users.py from this repository and paste it within users.py of your code_base.
  - Paste it at the bottom
  
  ---
### 4. actions.py
>   **path:**  deployements/2020-08-24-08-50-53/zproject/actions.py
  - The name of the file 2020-08-24-08-50-53 will be different in your case.
  - Copy the code from actions.py from this repository and paste it within actions.py of your code_base.
  - Paste it at the bottom
  
  ---
  ### After all the changes, restart the server.
  ### You are good to go!!!
  
Thank You 
Regards
Vijaykumar Gutala
