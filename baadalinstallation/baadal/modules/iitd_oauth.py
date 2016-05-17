from gluon.http import HTTP
from gluon.contrib.login_methods.oauth20_account import OAuthAccount
import hashlib
import random
CLIENT_ID="QdfJrpfrfmAVs15yXtsQBB1kCY7Oims8"
CLIENT_SECRET="AIS277umu5iW6ou3RXUszVNbUVZcislT"
AUTH_URL="http://oauth.cse.iitd.ac.in/authorize.php"
TOKEN_URL="http://oauth.cse.iitd.ac.in/token.php"
    
     
class IITD_Oauth(OAuthAccount):
        TOKEN_URL="http://oauth.cse.iitd.ac.in/token.php"
        AUTH_URL="http://oauth.cse.iitd.ac.in/authorize.php"
     
        def __init__(self):
            OAuthAccount.__init__(self,client_id-CLIENT_ID,client_secret=CLIENT_SECRET,auth_url=self.AUTH_URL,token_url=self.TOKEN_URL,scope='none')
     
       
     
        def get_user(self):
            if not self.accessToken():
                return None
            token=self.accessToken()
            #profile = app.get_profile(selectors=['id', 'first-name', 'last-name', 'email-address'])
            #if profile:
                #if not profile.has_key('username'):
                 #  username = profile['id']
                #else:
                 #   username = profile['username']
     
                #if not profile.has_key('emailAddress'):
                 #   email = '%s.fakemail' %(profile['id'])
                #else:
                 #   email = profile['emailAddress']
     
            return dict(first_name = "vipul",
                                last_name = "saxena")


