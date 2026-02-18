from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as auth_router
from smtp.smtp_router import router as smtp_router

app = FastAPI(title="AuthBrick API")

# ============================
# INCLUDE ROUTERS
# ============================
app.include_router(auth_router)
app.include_router(smtp_router)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, # True for allowing cookies from frontend
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}



