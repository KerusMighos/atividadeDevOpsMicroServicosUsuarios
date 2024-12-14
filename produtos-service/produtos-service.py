from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests, os

class ProductDTO(BaseModel):
    id: int
    name: str
    description: str
    price: float
    user_id: int

class ProductCreateDTO(BaseModel):
    name: str
    description: str
    price: float
    token: str

class UserAuthCheckDTO(BaseModel):
    name: str
    email: str
    id: int
    
class DeleteProductDTO(BaseModel):
    token: str
    product_id: int


class DB():
    products: list[ProductDTO] = [
        ProductDTO(id=1, name="Celular Samsung", description="Descrição do produto 1 ...", price=1000.0, user_id=1),
        ProductDTO(id=2, name="Televisão 23\"", description="Descrição do produto 2 ... ", price=2000.0, user_id=2),
        ProductDTO(id=3, name="Notebook Positivo", description="Descrição do produto 3 ... ", price=150.0, user_id=1),
        ProductDTO(id=4, name="Processador Ryzen", description="Descrição do produto 4 ... ", price=900.0, user_id=2),
        ProductDTO(id=5, name="Computador completo", description="Descrição do produto 5 ... ", price=600.0, user_id=1),
    ]
    id_counter = 5

    @staticmethod
    def find_product_by_id(product_id: int):
        for p in DB.products:
            if p.id == product_id:
                return p
        return None

    @staticmethod
    def delete_product_by_id(product_id: int):
        DB.products = [p for p in DB.products if p.id != product_id]

app = FastAPI()

def check_user_token(token: str) -> UserAuthCheckDTO:

    print("Verificando token de usuário: ", token)

    user_service_url = os.getenv("USER_SERVICE_URL", "localhost")
    user_service_port = os.getenv("USER_SERVICE_PORT", 8001)
    
    full_url = f"{user_service_url}:{user_service_port}/users/checkauth"


    response = requests.post(full_url, json={"token": token})
    
    
    if response.status_code != 200:
        print("Token invalido: ", token)
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    print("Token válido: ", token, response.json())
    return UserAuthCheckDTO(**response.json())


@app.get("/products", response_model=list[ProductDTO])
def list_products():
    print("Listando produtos")
    return DB.products


@app.post("/products", response_model=ProductDTO)
def create_product(product: ProductCreateDTO):

    user_info = check_user_token(product.token)

    DB.id_counter += 1
    new_product = ProductDTO(id=DB.id_counter, name=product.name, description=product.description, price=product.price, user_id=user_info.id)

    DB.products.append(new_product)

    print("Criando produto: ", new_product)

    return new_product


@app.delete("/products", response_model=ProductDTO)
def delete_product(product_to_delete: DeleteProductDTO):

    user_info = check_user_token(product_to_delete.token)

    product = DB.find_product_by_id(product_to_delete.product_id)
        
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if product.user_id != user_info.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para apagar este produto")

    print("Deletando produto: ", product)

    DB.delete_product_by_id(product_to_delete.product_id)

    return product

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PRODUTOS_SERVICE_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
