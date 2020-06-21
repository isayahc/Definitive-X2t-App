import logging
import os
""" add the other APIs when tidied up"""

class APIs:
    def __init__(self):
        self = self

    def getAlphaKey(self) ->str:
        alphaKey = os.getenv('ALPHA_KEY')
        return alphaKey

    def getTwilioCreditals(self) -> tuple:
        accountSid = os.getenv('TW_ACCOUNT_SID')
        authToken = os.getenv('TW_AUTH_TOKEN')
        return (accountSid,authToken)

    # https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html
    def getamazonCreditals(self) ->dict:
        cred = dict({
            'AWS_ACCESS_KEY_ID'.lower() : os.getenv('AWS_ACCESS_KEY_ID'),
            'AWS_SECRET_ACCESS_KEY'.lower() : os.getenv('AWS_SECRET_ACCESS_KEY'),
            'AWS_DEFAULT_REGION'.lower() : os.getenv('AWS_DEFAULT_REGION')

        })
        # AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
        # AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        # AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')

        return cred

api = APIs().getAlphaKey()