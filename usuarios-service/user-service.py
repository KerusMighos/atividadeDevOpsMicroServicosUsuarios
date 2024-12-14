from typing import Literal
from fastapi import FastAPI, HTTPException
import uuid
from pydantic import BaseModel, EmailStr

# Models =================================================================================================

class UserCreateDTO(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserModel(BaseModel):

    id: int
    name: str
    email: str
    password: str
    token: str
    
class UserAuthCheckDTO(BaseModel):
    name: str
    email: str
    id: int


class UserDetailDTO(BaseModel):
    name: str
    email: str

class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str
    
class TokenDTO(BaseModel):
    token: str

# Database =================================================================================================

class DB():

    users: list[UserModel] = [
        UserModel(id=1, name="João", email="joaozinho@gmail.com", password="123456", token="9b133aca-a372-4cd0-9e57-85bbf6910489"),
        UserModel(id=2, name="Maria", email="mariazinha@gmail.com", password="abcdef", token=""),
        UserModel(id=3, name="Carlos", email="carlos@gmail.com", password="654321", token=""),
        UserModel(id=4, name="Ana", email="ana@gmail.com", password="qwerty", token=""),
        UserModel(id=5, name="Pedro", email="pedro@gmail.com", password="zxcvbn", token="")
    ]

    id_counter = len(users)

    @staticmethod
    def findBy(key: Literal['id', 'username', 'email', 'password', 'token'], value: str):
        
        
        for u in DB.users:
            if getattr(u, key) == value:
                return u
        return None

# Utils =================================================================================================

def generate_token():
    return str(uuid.uuid4())

# Endpoints =================================================================================================

app = FastAPI()

@app.get("/users", response_model=list[UserDetailDTO])
def list_users():
    
    print('Listando usuários...')
    
    lista: list[UserDetailDTO] = []
    for u in DB.users:
        lista.append(UserDetailDTO(name=u.name, email=u.email))
    return lista



@app.post("/users", response_model=UserDetailDTO)
def create_user(user: UserCreateDTO):

    DB.id_counter += 1

    new_user = UserModel(id=DB.id_counter, 
                    name=user.name, 
                    email=user.email, 
                    password=user.password, 
                    token="")
    

    DB.users.append(new_user)

    print('Criando usuário: ', new_user)

    return UserDetailDTO(name=new_user.name, email=new_user.email)


@app.post("/users/login", response_model=TokenDTO)
def auth_user(user: UserLoginDTO):

    u = DB.findBy('email', user.email)

    if u is None:
        return {"detail": "Usuário não encontrado"}, 404

    if u.password != user.password:
        return {"detail": "Senha incorreta"}, 401

    t = generate_token()

    u.token = t

    print('Autenticando usuário: ', u, '\ntoken: ',t)

    return TokenDTO(token=t)


@app.post("/users/checkauth", response_model=UserAuthCheckDTO)
def check_auth(tokenDTO: TokenDTO):

    token = tokenDTO.token

    print('Verificando token de usuário: ', token)

    u = DB.findBy('token', token)

    if u is None:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    print(u)

    print('Token válido', u)

    return UserAuthCheckDTO(name=u.name, email=u.email, id=u.id)


if __name__ == "__main__":
    print("Produtos service rodando...")
    import uvicorn
    import os
    port = int(os.getenv("LISTEN_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    print("Produtos service finalizado.")

