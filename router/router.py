import logging

from models.schemas import RouteRequest, RouteResponse
from providers.mock import CheapMockProvider, MockProvider
from providers.openai import OpenAIProvider
from providers.gemini import GeminiProvider


logger = logging.getLogger(__name__)


class CostLatencyRouter:

    def __init__(self, providers=None):
        """
        Create a router with the supplied providers.

        If no providers are supplied, the router uses
        the default provider set.
        """

        self.providers = (
            providers
            if providers is not None
            else [
                CheapMockProvider(),
                MockProvider(),
                OpenAIProvider(),
                GeminiProvider(),
            ]
        )

    def route(self, request: RouteRequest) -> RouteResponse:

        eligible_providers = []

        # ---------------------------------------------------------
        # 1. Estimate cost and latency
        # ---------------------------------------------------------

        for provider in self.providers:

            try:

                estimated_cost = provider.estimate_cost(
                    request.prompt
                )

                estimated_latency = provider.estimate_latency()

                logger.debug(
                    "Provider evaluated | provider=%s | model=%s | "
                    "cost=%s | latency_ms=%s",
                    provider.name,
                    provider.model,
                    estimated_cost,
                    estimated_latency,
                )

                # -------------------------------------------------
                # 2. Check constraints
                # -------------------------------------------------

                if (
                    estimated_cost <= request.max_cost
                    and estimated_latency <= request.max_latency_ms
                ):

                    eligible_providers.append(
                        (
                            provider,
                            estimated_cost,
                            estimated_latency,
                        )
                    )

            except Exception as exc:

                logger.warning(
                    "Provider '%s' failed during estimation: %s",
                    provider.name,
                    exc,
                )

        # ---------------------------------------------------------
        # 3. No provider satisfies requirements
        # ---------------------------------------------------------

        if not eligible_providers:

            raise ValueError(
                "No provider satisfies the cost and latency requirement."
            )

        # ---------------------------------------------------------
        # 4. Cheapest provider first
        # ---------------------------------------------------------

        eligible_providers.sort(
            key=lambda item: item[1]
        )

        # ---------------------------------------------------------
        # 5. Try providers in cost order
        # ---------------------------------------------------------

        for (
            provider,
            estimated_cost,
            estimated_latency,
        ) in eligible_providers:

            try:

                provider.generate(
                    request.prompt
                )

                logger.info(
                    "Provider selected | provider=%s | model=%s | "
                    "cost=%s | latency_ms=%s",
                    provider.name,
                    provider.model,
                    estimated_cost,
                    estimated_latency,
                )

                return RouteResponse(
                    provider=provider.name,
                    model=provider.model,
                    estimated_cost=estimated_cost,
                    estimated_latency_ms=estimated_latency,
                    reason=(
                        "Cheapest eligible provider selected "
                        "within cost and latency constraints."
                    ),
                )

            except Exception as exc:

                logger.warning(
                    "Provider '%s' failed during generation: %s",
                    provider.name,
                    exc,
                )

                continue

        # ---------------------------------------------------------
        # 6. All eligible providers failed
        # ---------------------------------------------------------

        raise ValueError(
            "All eligible providers failed during generation."
        )