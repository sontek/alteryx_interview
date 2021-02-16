import csv
import orjson
import pandas as pd
from dateutil.parser import parse as parsedate
from pathlib import Path
from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Header,
    Depends,
    HTTPException,
)
from datetime import date
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .settings import Settings, get_settings
from .db import ORM

cwd = Path(__file__).parents[0]
df = pd.read_json(cwd / 'top100.json')
df["date"] = pd.to_datetime(df["date"]).dt.date

orm = ORM('stocks.db')
orm.migrations()
app = FastAPI()

# TODO: figure out how to load this lazily...
# origins = [f"http://{settings.Config.API_ORIGIN}"]
origins = []

# limit file uploads to 50mb
MAX_SIZE: int = 50 * 1_024 ** 2

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def valid_content_length(
    content_length: int = Header(..., lt=MAX_SIZE)
):
    return content_length


@app.put("/user/{username}/portfolio")
async def create_portfolio(
    username: str,
    file: UploadFile = File(...),
    file_size: int = Depends(valid_content_length),
    settings: Settings = Depends(get_settings),
):
    file.file.seek(0)
    data = file.file.read()
    reader = csv.DictReader(data.decode('utf-8').split('\n'))
    orm.clear_holdings(username)
    for row in reader:
        current_date = parsedate(row['date']).date()
        nearest = df.loc[
            df['date'].sub(current_date).abs().idxmin()
        ]['date']
        current_price = float(df.loc[
            (df['date'] == nearest) &
            (df['Name'] == row['symbol'])
        ]['low'])
        orm.change_stock(
            current_date,
            username,
            row['symbol'],
            'buy',
            row['quantity'],
            current_price,
        )
    return {}


class User(BaseModel):
    username: str
    first: str
    last: str
    budget: float

@app.post("/user")
async def create_user(
    user: User,
    settings: Settings = Depends(get_settings),
):
    existing = orm.get_user(
        user.username,
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail='Username is already in use'
        )
    orm.create_user(
        user.username, user.first, user.last, user.budget
    )
    return {
        "success": True,
        "user": jsonable_encoder(user),
    }


class UpdateUser(BaseModel):
    first: Optional[str] = None
    last: Optional[str] = None
    budget: Optional[float] = None

@app.patch("/user/{username}")
async def update_user(
    username: str,
    updated_user: UpdateUser,
    settings: Settings = Depends(get_settings),
):
    user = User(**orm.get_user(
        username,
    ))
    update_data = updated_user.dict(exclude_unset=True)
    final_user = user.copy(
        update=update_data
    )
    orm.update_user(
        final_user.username,
        final_user.first,
        final_user.last,
        final_user.budget
    )
    return {
        'success': True,
        'user': jsonable_encoder(final_user),
    }


class Stock(BaseModel):
    date: date
    symbol: str
    quantity: int


@app.post("/stocks/{username}/buy")
async def buy(
    username: str,
    stock: Stock,
    settings: Settings = Depends(get_settings),
):
    current_price = float(df.loc[
        (df['date'] == stock.date) &
        (df['Name'] == stock.symbol)
    ]['low'])

    cost_to_buy = current_price * stock.quantity
    user = User(**orm.get_user(
        username,
    ))

    if cost_to_buy > user.budget:
        raise HTTPException(
            status_code=400,
            detail="Can't spend more than you have"
        )

    orm.change_stock(
        stock.date,
        username,
        stock.symbol,
        'buy',
        stock.quantity,
        current_price,
    )
    balance = user.budget - cost_to_buy
    orm.update_budget(username, balance)
    return {
        "success": True,
        "cost": cost_to_buy,
        "balance": balance,
    }


@app.post("/stocks/{username}/sell")
async def sell(
    username: str,
    stock: Stock,
    settings: Settings = Depends(get_settings),
):
    current_price = float(df.loc[
        (df['date'] == stock.date) &
        (df['Name'] == stock.symbol)
    ]['low'])

    value_to_sell = current_price * stock.quantity

    user = User(**orm.get_user(
        username,
    ))

    holdings = orm.get_holdings(username, stock.symbol)

    if not holdings or holdings < stock.quantity:
        raise HTTPException(
            status_code=400,
            detail="Can't sell more than you have"
        )

    orm.change_stock(
        stock.date,
        username,
        stock.symbol,
        'sell',
        stock.quantity * -1,
        current_price * -1,
    )
    balance = user.budget + value_to_sell
    orm.update_budget(username, balance)

    return {
        "success": True,
        "value": value_to_sell,
        "balance": balance,
    }


@app.get("/user/{username}/portfolio")
async def portfolio(
    username: str,
    filter_date: date,
    settings: Settings = Depends(get_settings),
):
    values = {}
    holdings = orm.get_total_holdings(
        username,
        filter_date,
    )
    for hold in holdings:
        symbol = hold[0]
        amount = hold[1]
        nearest = df.loc[
            df['date'].sub(filter_date).abs().idxmin()
        ]['date']
        current_price = float(df.loc[
            (df['date'] == nearest) &
            (df['Name'] == symbol)
        ]['low'])
        values[symbol] = "{:.2f}".format(amount * current_price)

    return {
        "success": True,
        "values": values,
    }
