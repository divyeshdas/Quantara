from fastapi import APIRouter
from pydantic import BaseModel

from data.rbi_provider import get_historical_for_api, get_current_rate

router = APIRouter()


class RatePoint(BaseModel):
    date: str
    rate: float


class HistoricalRatesResponse(BaseModel):
    data: list[RatePoint]
    current_rate: float
    data_source: str


@router.get("/historical", response_model=HistoricalRatesResponse)
async def get_historical_rates():
    history = get_historical_for_api()
    current = get_current_rate()
    return HistoricalRatesResponse(
        data=[RatePoint(**p) for p in history],
        current_rate=current,
        data_source="RBI DBIE",
    )
