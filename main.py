# main.py
import logging
import zoneinfo
from datetime import datetime

from fastapi import FastAPI, HTTPException
from models import Customer, CustomerCreate, Transaction, Invoice
from db import SessionDep, create_all_tables
from sqlmodel import select

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("../logs/app.log"),
        logging.StreamHandler(), 
    ],
)

app_logger = logging.getLogger("fastapi")
sql_logger = logging.getLogger("sqlalchemy.engine")

sql_logger.setLevel(logging.DEBUG)

try:
    app = FastAPI(lifespan=create_all_tables)
except Exception as e:
    app_logger.error("Error FastAPI ", exc_info=True)




@app.get("/")
async def root():
    return {"message": "Bye Ali 2"}

timezones_supported = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "AR": "America/Argentina/Buenos_Aires",
    "NY": "America/New_York",
    "JP": "Asia/Tokyo",
}

@app.get("/get-time/{iso_code}")
async def get_time(iso_code: str):
    iso = iso_code.upper()
    timezone_str = timezones_supported.get(iso)
    if not timezone_str:
        return {"error": "ISO Code no soportado"}
    try:
        tz = zoneinfo.ZoneInfo(timezone_str)
        return {"time": datetime.now(tz)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la zona horaria: {str(e)}")



db_customer: list[Customer] = []
@app.post("/customers", response_model=Customer)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):    
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)    
    return customer


@app.get("/customers", response_model=list[Customer])
async def list_customers(session: SessionDep):
    return session.exec(select(Customer)).all()


@app.post("/transactions")
async def create_transaction(transaction_data: Transaction):
    return transaction_data



@app.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data
