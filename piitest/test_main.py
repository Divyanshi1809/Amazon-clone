
##from main import UserManager


#@pytest.fixture
#def user_manager():
    #"""Creates a fresh instance of UserManager before each test."""
    #return UserManager()


#def test_add_user(user_manager):
    #assert user_manager.add_user("john_doe", "john@example.com") == True
    #assert user_manager.get_user("john_doe") == "john@example.com"


#def test_add_duplicate_user(user_manager):
 #   user_manager.add_user("john_doe", "john@example.com")
  #  with pytest.raises(ValueError):
   #     user_manager.add_user("john_doe", "john@example.com")


# Alternately, test fails if we define global variable:


#user_manager = UserManager()


#def test_add_user():
 #    assert user_manager.add_user("john_doe", "john@example.com") == True
  #   assert user_manager.get_user("john_doe") == "john@example.com"


#def test_add_duplicate_user():
  #   user_manager.add_user("john_doe", "john@example.com")
   #  with pytest.raises(ValueError):
    #     user_manager.add_user("john_doe", "john@example.com")




import pytest
from main import get_weather


# pip install pytest
# pip install pytest-mock


def test_get_weather(mocker):
    # Mock requests.get
    mock_get = mocker.patch("main.requests.get")


    # Set return values
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"temperature": 25, "condition": "Sunny"}


    # Call function
    result = get_weather("Dubai")


    # Assertions
    assert result == {"temperature": 25, "condition": "Sunny"}
    mock_get.assert_called_once_with("https://api.weather.com/v1/Dubai")