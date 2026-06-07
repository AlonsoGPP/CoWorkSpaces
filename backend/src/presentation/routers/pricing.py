from fastapi import APIRouter, Depends

from application.dto.pricing_dto import QuoteReservationPriceInputDTO
from application.use_cases.quote_reservation_price import QuoteReservationPriceUseCase
from presentation.dependencies import get_quote_reservation_price_use_case
from presentation.schemas.pricing import PricingQuoteRequest, PricingQuoteResponse

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.post("/quote", response_model=PricingQuoteResponse)
def quote_reservation_price(
    payload: PricingQuoteRequest,
    use_case: QuoteReservationPriceUseCase = Depends(
        get_quote_reservation_price_use_case
    ),
) -> PricingQuoteResponse:
    output = use_case.execute(
        QuoteReservationPriceInputDTO(
            space_id=payload.space_id,
            start_at=payload.start_at,
            end_at=payload.end_at,
        )
    )
    return PricingQuoteResponse.model_validate(output)
