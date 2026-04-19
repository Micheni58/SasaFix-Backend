from pydantic import BaseModel
from typing import Optional, List
from datetime import time

class ProviderSearchParams(BaseModel):
    """
    Query parameters accepted by GET /api/discovery/providers
    All fields optional — omitting a field means "no filter on this"
    """
    category: Optional[str] = None
    search: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: float = 10.0
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    page: int = 1
    page_size: int = 12

class GeocodeRequest(BaseModel):
    address: str

class ProviderServiceSchema(BaseModel):
    id: int
    service_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class AvailabilitySlotSchema(BaseModel):
    id: int
    day_of_week: str
    start_time: time
    end_time: time
    is_booked: bool

    class Config:
        from_attributes = True


class ProviderCardSchema(BaseModel):
    """
    Compact schema — used for the Find Services grid cards.
    Contains just enough to render a card without extra DB calls.
    """
    id: int
    user_id: int
    first_name: str
    last_name: str
    profile_photo_url: Optional[str] = None
    bio: Optional[str] = None
    service_category: Optional[str] = None
    hourly_rate: Optional[float] = None
    average_rating: Optional[float] = None
    total_reviews: int = 0
    total_jobs_completed: int = 0
    is_verified: bool = False
    is_premium: bool = False
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_km: Optional[float] = None
    services: List[ProviderServiceSchema] = []

    class Config:
        from_attributes = True


class ProviderDetailSchema(ProviderCardSchema):
    """
    Full schema — used for the public profile page.
    Extends ProviderCardSchema with extra fields + availability.
    """
    years_of_experience: Optional[int] = None
    response_time_minutes: Optional[int] = None
    member_since: Optional[str] = None
    verification_status: str = "pending"
    availability: List[AvailabilitySlotSchema] = []

    class Config:
        from_attributes = True


class ProviderListResponse(BaseModel):
    """
    Paginated response for the Find Services page.
    Includes both the paginated grid AND the premium featured section.
    """
    providers: List[ProviderCardSchema]
    premium_providers: List[ProviderCardSchema]   # for top featured row
    total: int
    page: int
    page_size: int
    total_pages: int


class GeocodeResponse(BaseModel):
    latitude: float
    longitude: float
    formatted_address: str


class LocationSuggestion(BaseModel):
    place_id: str
    description: str


class LocationSuggestionsResponse(BaseModel):
    suggestions: List[LocationSuggestion]


class CategoriesResponse(BaseModel):
    categories: List[str]
