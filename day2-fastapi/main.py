from pydantic import BaseModel, field_validator, ValidationError
from datetime import datetime
class User(BaseModel):
    first_name: str
    last_name: str

    @field_validator("first_name","last_name")
    @classmethod
    def santizeUser(cls, name):
        santized_user_details = name.strip()
        if not santized_user_details:
            raise ValueError("name cannot be empty")
        return santized_user_details
    
    def get_user(user_id:str):
        if user_id <=0:
            raise InvalidUserError(f"cannot be zero")

class InvalidUserError(Exception):
    pass


try:
    user = User(first_name="", last_name="")
    result = santizeUser
    print(f"User created:{user.first_name} {user.last_name}")

except ValidationError  as Err:
   print(f"Validation failed: {Err}")

finally:
    print("UserDetails Entered Successfully")


class InvalidUserTime(Exception):
    pass

def santizeTime(time:str):
 
    if not isinstance(time, str):
        raise InvalidUserTime(f"expected string but got {type(time).__name__}") 
    
     if not time:
        raise InvalidUserTime(f"Time should not be empty")

    #check format

    try:
        parsed = datetime.strptime(time,"%Y-%m-%d")

    except ValueError:
        raise InvalidUserTime(f"expected format is not matching, received {time}\n Excepted should Y-M-D")
    

    return time

   

try:
    time = santizeTime("2024-9-20")

except InvalidUserTime as Err:
    print(f"Validation failed,{Err}")

finally:
    print("User Entered Valid time only")
