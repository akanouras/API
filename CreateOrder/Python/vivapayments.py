#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import datetime
import json
import math
from base64 import standard_b64encode
import re

try:
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
except ImportError:  # Python 2
    from urllib2 import Request, urlopen
    from urllib import urlencode


class VivaPayments(object):
    """VivaPayments API Wrapper"""

    # Demo constants
    DEMO_URL = 'http://demo.vivapayments.com/api/'
    DEMO_REDIRECT_URL = 'http://demo.vivapayments.com/web/checkout?ref='

    # Production constants
    PRODUCTION_URL = 'https://www.vivapayments.com/api/'
    PRODUCTION_REDIRECT_URL = 'https://www.vivapayments.com/web/checkout?ref='
    
    def __init__(self,merchant_id=None,api_key=None,production=False):
        self.url = self.PRODUCTION_URL if production else self.DEMO_URL
        self.merchant_id=merchant_id
        self.api_key=api_key

    def create_order(self,amount,**kwargs):
        """Create a Payment Order."""
        data = self.pack_data('amount',amount,kwargs)
        return self._request('POST','orders',data)

    def cancel_order(self,order_code,**kwargs):
        """Cancel an existing Payment Order."""
        data = self.pack_data('order_code',order_code,kwargs)
        return self._request('DELETE','orders/'+str(order_code),data)

    def get_transaction(self,transaction_id,**kwargs):
        """Get all details for a specific transaction, or for all transactions of a given date."""
        data = self.pack_data('transaction_id',transaction_id,kwargs)
        return self._request('GET','transactions/'+str(transaction_id),data)

    def create_recurring_transaction(self,transaction_id,**kwargs):
        """Make a recurring transaction."""
        data = self.pack_data('transaction_id',transaction_id,kwargs)
        return self._request('POST','transactions/'+str(transaction_id),data)

    def cancel_transaction(self,transaction_id,amount):
        """Cancel or refund a payment."""
        return self._grequest('DELETE','transactions/'+str(transaction_id)+'?amount='+str(amount))
   
    def get_redirect_url(self,order_code):
        """Returns the order code appended on the REDIRECT_URL_PREFIX"""
        redirect_url = self.DEMO_REDIRECT_URL if self.url == self.DEMO_URL else self.PRODUCTION_REDIRECT_URL
        return redirect_url+str(order_code)

    ### UTILITY FUNCTIONS ###
    def pack_data(self,arg_name,arg_val,kwargs):
        data = {arg_name: arg_val}
        data.update(kwargs)
        return data

    def _grequest(self,request_method,url_suffix):
        # Construct request object
        request_url = self.url + url_suffix
        request = Request(request_url)
        
        # Request basic access authentication
        base64string = standard_b64encode('{0}:{1}'.format(
            self.merchant_id, self.api_key).encode()).decode().strip()
        request.add_header("Authorization", "Basic %s" % base64string)   
        
        # Set http request method
        request.get_method = lambda: request_method
        response = urlopen(request)
        return self._decode(response.read().decode())

    def _request(self,request_method,url_suffix,data):
        # Construct request object
        data = urlencode(data).encode()
        request_url = self.url + url_suffix
        request = Request(request_url,data=data)
        
        # Request basic access authentication
        base64string = standard_b64encode('{0}:{1}'.format(
            self.merchant_id, self.api_key).encode()).decode().strip()
        request.add_header("Authorization", "Basic %s" % base64string)   
        
        # Set http request method
        request.get_method = lambda: request_method
        response = urlopen(request)
        return self._decode(response.read().decode())

    def _decode(self,json_response):
        obj = json.loads(json_response)
        
        timestamp = obj['TimeStamp']

        # This regex takes care of 2 things:
        # - The fractional part of seconds ends up as integer microseconds (exactly 6 digits)
        # - The UTC offset becomes +0300 from +03:00, as strptime likes it
        timestamp_fixed = re.sub(r'\.([0-9]{6})[0-9]*([-+][0-9]{2}):([0-9]{2})$', r'.\1\2\3', timestamp)

        obj['TimeStamp'] = datetime.datetime.strptime(timestamp_fixed, '%Y-%m-%dT%H:%M:%S.%f%z')

        return obj

# Examples
if __name__ == '__main__':
    # Create vivapayments API Wraper
    viva_payments = VivaPayments(merchant_id='1b2573e7-2f67-4443-8a2e-84cac16ec79f',api_key='09014933')
    
    # Example 1

    # Create order 
    result = viva_payments.create_order(100,RequestLang='en-US')
    
    # Get order code
    order_code = result['OrderCode']

    # Get redirect url
    redirect_url = viva_payments.get_redirect_url(order_code)

    # Get the redirect url and paste it at your browser
    print(redirect_url)

    # Example 2
    # Cancel Transaction

    result = viva_payments.cancel_transaction('959A0471-2CC8-4E75-A422-97E318E48ACD', 10)
    print(result)


