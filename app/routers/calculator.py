from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal
import math

router = APIRouter(prefix="/calculator", tags=["Hydration Calculator"])

COUNTRY_CLIMATE = {
    "Nigeria": "hot", "Ghana": "hot", "Senegal": "hot", "Mali": "hot",
    "Burkina Faso": "hot", "Niger": "hot", "Chad": "hot", "Sudan": "hot",
    "Ethiopia": "hot", "Somalia": "hot", "Djibouti": "hot", "Eritrea": "hot",
    "South Sudan": "hot", "Central African Republic": "hot", "Cameroon": "hot",
    "Togo": "hot", "Benin": "hot", "Guinea": "hot", "Guinea-Bissau": "hot",
    "Sierra Leone": "hot", "Liberia": "hot", "Ivory Coast": "hot",
    "Gambia": "hot", "Mauritania": "hot", "Angola": "hot", "Mozambique": "hot",
    "Zambia": "hot", "Zimbabwe": "hot", "Malawi": "hot", "Tanzania": "hot",
    "Congo": "hot", "DR Congo": "hot", "Gabon": "hot", "Equatorial Guinea": "hot",
    "Namibia": "hot", "Botswana": "hot", "Eswatini": "hot",
    "Kenya": "moderate", "Uganda": "moderate", "Rwanda": "moderate",
    "Burundi": "moderate", "South Africa": "moderate", "Lesotho": "moderate",
    "Egypt": "moderate", "Morocco": "moderate", "Algeria": "moderate",
    "Tunisia": "moderate", "Libya": "moderate", "Madagascar": "moderate",
    "Mauritius": "moderate", "Cape Verde": "moderate", "Comoros": "moderate",
    "Seychelles": "moderate", "Sao Tome and Principe": "moderate",
}

AFRICAN_COUNTRIES = sorted(COUNTRY_CLIMATE.keys())
ACTIVITY_MULTIPLIERS = {"low": 1.0, "medium": 1.2, "high": 1.5}
CLIMATE_MULTIPLIERS = {"hot": 1.3, "moderate": 1.1}
BOTTLE_SIZE_ML = 500


class HydrationRequest(BaseModel):
    country: str
    activity_level: Literal["low", "medium", "high"]
    weight_kg: int


class HydrationResponse(BaseModel):
    country: str
    activity_level: str
    weight_kg: int
    climate_type: str
    daily_water_ml: int
    daily_water_litres: float
    hydra_bottles_per_day: int
    hydra_bottles_per_week: int
    recommendation: str
    tip: str


@router.get("/countries")
def get_countries():
    return {"countries": AFRICAN_COUNTRIES}


@router.post("/calculate", response_model=HydrationResponse)
def calculate_hydration(payload: HydrationRequest):
    country = payload.country if payload.country in COUNTRY_CLIMATE else "Nigeria"
    climate = COUNTRY_CLIMATE[country]
    base_ml = payload.weight_kg * 35
    daily_water_ml = int(base_ml * ACTIVITY_MULTIPLIERS[payload.activity_level] * CLIMATE_MULTIPLIERS[climate])
    daily_water_litres = round(daily_water_ml / 1000, 1)
    bottles_per_day = math.ceil(daily_water_ml / BOTTLE_SIZE_ML)
    bottles_per_week = bottles_per_day * 7

    recommendation = (
        f"Based on your weight ({payload.weight_kg}kg), {payload.activity_level} activity, "
        f"and {climate} climate in {country}, you need {daily_water_litres}L of water daily. "
        f"That's {bottles_per_day} bottle(s) of HYDRA per day."
    )

    tips = {
        ("hot", "high"): "Hot climate + high activity — hydrate before, during, and after. Never wait until you're thirsty.",
        ("hot", "medium"): "Hot climates cause faster fluid loss than you realise. Keep a HYDRA bottle with you at all times.",
        ("hot", "low"): "Even low activity in a hot climate causes passive fluid loss. Start your day with HYDRA.",
        ("moderate", "high"): "High activity demands consistent hydration. HYDRA's electrolytes help muscles recover faster.",
        ("moderate", "medium"): "Consistent hydration keeps you focused and energised throughout the day.",
        ("moderate", "low"): "Stay consistent — daily hydration keeps you mentally sharp even on quiet days.",
    }

    tip = tips.get((climate, payload.activity_level), "Drink consistently throughout the day for best results.")

    return HydrationResponse(
        country=country, activity_level=payload.activity_level, weight_kg=payload.weight_kg,
        climate_type=climate, daily_water_ml=daily_water_ml, daily_water_litres=daily_water_litres,
        hydra_bottles_per_day=bottles_per_day, hydra_bottles_per_week=bottles_per_week,
        recommendation=recommendation, tip=tip,
    )