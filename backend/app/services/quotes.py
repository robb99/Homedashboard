import logging
from typing import List, Optional, Tuple

import httpx

from app.models.schemas import QuoteItem, QuotesResponse

logger = logging.getLogger(__name__)

QUOTABLE_URL = "https://api.quotable.io/quotes/random?limit=5"
ZENQUOTES_URL = "https://zenquotes.io/api/quotes"

FALLBACK_QUOTES = [
    QuoteItem(text="The only way to do great work is to love what you do.", author="Steve Jobs"),
    QuoteItem(text="In the middle of difficulty lies opportunity.", author="Albert Einstein"),
    QuoteItem(text="The best way to predict the future is to create it.", author="Peter Drucker"),
    QuoteItem(text="Be the change that you want to see in the world.", author="Mahatma Gandhi"),
    QuoteItem(text="Through discipline comes freedom.", author="Aristotle"),
]


async def _fetch_quotable(client: httpx.AsyncClient) -> Tuple[Optional[List[QuoteItem]], Optional[str]]:
    try:
        response = await client.get(QUOTABLE_URL)
        if response.status_code >= 400:
            return None, f"Quotable HTTP {response.status_code}"
        data = response.json()
        if not isinstance(data, list) or len(data) == 0:
            return None, "Quotable returned an empty or invalid payload"
        quotes = [
            QuoteItem(text=item.get("content", ""), author=item.get("author"))
            for item in data
            if item.get("content")
        ]
        if not quotes:
            return None, "Quotable returned no usable quotes"
        return quotes, None
    except Exception as exc:
        return None, f"Quotable request failed: {exc}"


async def _fetch_zenquotes(client: httpx.AsyncClient) -> Tuple[Optional[List[QuoteItem]], Optional[str]]:
    try:
        response = await client.get(ZENQUOTES_URL)
        if response.status_code >= 400:
            return None, f"ZenQuotes HTTP {response.status_code}"
        data = response.json()
        if not isinstance(data, list) or len(data) == 0:
            return None, "ZenQuotes returned an empty or invalid payload"
        quotes = [
            QuoteItem(text=item.get("q", ""), author=item.get("a"))
            for item in data[:5]
            if item.get("q")
        ]
        if not quotes:
            return None, "ZenQuotes returned no usable quotes"
        return quotes, None
    except Exception as exc:
        return None, f"ZenQuotes request failed: {exc}"


class QuotesService:
    async def get_quotes(self) -> QuotesResponse:
        async with httpx.AsyncClient(timeout=10.0) as client:
            quotable_quotes, quotable_error = await _fetch_quotable(client)
            if quotable_quotes:
                return QuotesResponse(
                    quotes=quotable_quotes,
                    source="quotable",
                    fallback=False,
                    reason=None,
                )

            logger.warning(f"Quotes fallback to ZenQuotes: {quotable_error}")
            zenquotes_quotes, zenquotes_error = await _fetch_zenquotes(client)
            if zenquotes_quotes:
                return QuotesResponse(
                    quotes=zenquotes_quotes,
                    source="zenquotes",
                    fallback=True,
                    reason=quotable_error,
                )

            reason = f"Quotable failed: {quotable_error}; ZenQuotes failed: {zenquotes_error}"
            logger.error(f"Quotes fallback to local data: {reason}")
            return QuotesResponse(
                quotes=FALLBACK_QUOTES,
                source="fallback",
                fallback=True,
                reason=reason,
            )


quotes_service = QuotesService()
