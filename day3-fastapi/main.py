fake_db = [
    {"id": 1, "name": "Shoes", "price": 499.99, "stock": 10},
    {"id": 2, "name": "Shirt", "price": 299.99, "stock": 5},
    {"id": 3, "name": "Bag",   "price": 999.99, "stock": 2},
]

from fastapi import FastAPI, HTTPException, Request, Depends, Header, BackgroundTasks    
from pydantic import BaseModel
from routers import users
from fastapi.responses import JSONResponse
import time
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],                      # GET, POST, PUT, DELETE
    allow_headers=["*"],                      # Authorization, Content-Type
)

app.include_router(users.router)

#schema
class Product(BaseModel):
    name:str
    price:float
    stock:int=0



class ProductNotFoundError(Exception):
    def __init__(self, product_id:int):
        self.product_id=product_id
        super().__init__(f"product {product_id} not found")

class InvalidPriceError(Exception):
    def __init__(self, price:float):
        super().__init__(f"price {price} must be greater than 0")

@app.exception_handler(InvalidPriceError)
async def invalid_price_handler(request:Request, exec: InvalidPriceError):
    return JSONResponse(
        status_code=400,
        content={
            'error_code':400,
            'message':str(exec),
            'success':False
        }
    )

@app.exception_handler(ProductNotFoundError)
async def product_not_found_handler(request:Request, exc:ProductNotFoundError):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error_code": 404,
            "message": str(exc)
        }
    )


def get_product_or_404(product_id: int):
    for item in fake_db:
        if item['id'] == product_id:
            return item
    raise ProductNotFoundError(product_id)
    
@app.get("/")
def greet():
    return {
        "message" : "Welcome Home"
    }

#with path params
@app.get("/products/{product_id}")
def product_details(product_id: int):
        product = get_product_or_404(product_id)
        return product
    

#query params
@app.get("/product-list")
def product_list(skip:int=0, limit:int=10):
    return{
        "data":[],
        "skip":skip,
        "limit":limit,
        "totoal_result":10
    }

#excersise

@app.get("/users/{user_id}")
def get_user_details(user_id:int)->dict:
    return{
        "user_id": user_id,
        "name":"Abi"
    }

@app.get("/users")
def get_user_list(skip:int=0, limit:int=5)->dict:
    return{
        "data":[],
        "skip":skip,
        "limit":limit,
        "totoal_results":10
    }


#post method
@app.post("/products",status_code=201)
def create_product(product:Product)->dict:
    if product.price <= 0:
        raise InvalidPriceError(product.price)
    return {
            "message":"Product created successfully",
            "details": product
        }
#put method
@app.put("/products/{product_id}", status_code=200)
def update_product(product_id: int, product: Product) -> dict:
    for item in fake_db:                    # ✅ use "item" not "product"
        if item["id"] == product_id:
            item.update(product.model_dump())  # ✅ one line update
            return {
                "message": "product updated",
                "product_id": product_id,
                "details": item
            }
    raise HTTPException(status_code=404, detail="product not found")

#delete method
@app.delete("/product/{product_id}",status_code=200)
def delete_product(product_id:int) -> dict:
    for item in fake_db:
        if item["id"] == product_id:
           fake_db.remove(item)
           return {
            "message":"Deleted successfully"
           }
    raise HTTPException(status_code=404, detail="Product not found")


@app.middleware('http')
async def logMiddleware(request:Request,route):
     start = time.time()
     print(f"{request.method} {request.url.path}")
     response = await route(request)
     duration = time.time() - start
     print(f"← done in {duration:.3f}s")
     return response


def verify_token(token:str=Header()):
    if token=="mytoken123":
        return token
    raise HTTPException(status_code=401,detail="token doesnt match")

@app.get("/secure-products")
def secure_products(token:str=Depends(verify_token)):
    return fake_db


class UserCreate(BaseModel):
    name:str
    email:str
    password:str

def send_welcome_email(email:str):
    print(f"sending welcome email to {email}")
    time.sleep(2)
    print(f"email sent to {email}")

@app.post("/register",status_code=201)
async def register(user:UserCreate,background_task: BackgroundTasks):
    background_task.add_task(send_welcome_email, user.email)
    return {"message": "registered successfully", "name": user.name}