#def add(a, b):
    #return a+b


#def divide(a, b):
    #if b == 0:
       # raise ZeroDivisionError("Cannot divide by zero")
    #return a/b




#class UserManager:
   # def __init__(self):
    #    self.users = {}
   
    #def add_user(self, username, email):
     #   if username in self.users:
      #      raise ValueError("User already exists")
       # self.users[username] = email
        #return True
   
   # def get_user(self, username):
        # return self.users[username]
    #    return self.users.get(username)







import requests


def get_weather(city):
    response = requests.get(f"https://api.weather.com/v1/{city}")
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Could not fetch weather data")
