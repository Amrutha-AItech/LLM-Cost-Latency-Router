# LLM Cost & Latency Router

A modular LLM routing service that evaluates multiple language model providers based on estimated cost and latency, applies request constraints, and selects an eligible provider through a common provider abstraction.

## Overview

Modern AI applications may use multiple LLM providers with different pricing, latency, availability, and capabilities.

This project introduces a routing layer between the application and LLM providers.

The router evaluates configured providers, filters them according to cost and latency requirements, orders eligible providers by estimated cost, and attempts generation with eligible providers.

If a provider fails during generation, the router can continue with another eligible provider.

## Features

- Multi-provider LLM architecture
- Provider abstraction using an abstract base class
- OpenAI provider integration
- Gemini provider integration
- Mock providers for testing
- Cost estimation
- Latency estimation
- Maximum-cost constraints
- Maximum-latency constraints
- Cost-based provider selection
- Provider fallback during generation
- FastAPI API layer
- Pydantic request/response schemas
- Automated pytest test suite
- Environment-based API key configuration
- Structured logging
- Extensible provider architecture

## Architecture

Client
  |
  v
FastAPI API
  |
  v
Cost & Latency Router
  |
  +----------------------+----------------------+
  |                      |                      |
  v                      v                      v
OpenAI Provider      Gemini Provider       Mock Providers
  |                      |                      |
  v                      v                      v
OpenAI API            Gemini API          Local Testing

## Request Flow

1. Client sends a routing request.
2. FastAPI validates the request.
3. The router evaluates every configured provider.
4. Each provider's estimated cost is calculated.
5. Each provider's estimated latency is calculated.
6. Providers that exceed the request constraints are excluded.
7. Eligible providers are sorted by estimated cost.
8. The router attempts generation starting with the cheapest eligible provider.
9. If generation succeeds, routing information is returned.
10. If generation fails, the router attempts the next eligible provider.
11. If every eligible provider fails, the router raises an error.

## Provider Abstraction

The provider interface is defined in:

`providers/base.py`

Every provider implements:

- `name`
- `model`
- `generate(prompt)`
- `estimate_cost(prompt)`
- `estimate_latency()`

This allows the router to work with different LLM providers without depending on provider-specific implementation details.

The architecture is:

LLMProvider
  |
  +-- OpenAIProvider
  |
  +-- GeminiProvider
  |
  +-- MockProvider
  |
  +-- CheapMockProvider

## OpenAI Provider

The OpenAI implementation is located at:

`providers/openai.py`

Responsibilities:

- Load `OPENAI_API_KEY` from the environment.
- Create the OpenAI client.
- Expose the provider name.
- Expose the model name.
- Generate responses through the OpenAI API.
- Estimate cost.
- Estimate latency.

## Gemini Provider

The Gemini implementation is located at:

`providers/gemini.py`

Responsibilities:

- Load `GEMINI_API_KEY` from the environment.
- Create the Gemini client.
- Expose the provider name.
- Expose the model name.
- Generate responses through the Gemini API.
- Estimate cost.
- Estimate latency.

The Gemini provider loads the environment file from the project root so that the API key is available regardless of the provider module's location.

## Mock Providers

The mock implementations are located at:

`providers/mock.py`

The project includes:

- `CheapMockProvider`
- `MockProvider`

These providers return deterministic responses and predictable cost/latency values.

They allow routing behavior to be tested without depending on external APIs, network connectivity, API quotas, or real LLM responses.

## Routing Logic

The routing implementation is located at:

`router/router.py`

The router performs the following operations:

### 1. Provider Evaluation

Every configured provider is evaluated.

### 2. Cost Estimation

The router calls:

`provider.estimate_cost(request.prompt)`

### 3. Latency Estimation

The router calls:

`provider.estimate_latency()`

### 4. Constraint Checking

A provider is eligible only when:

`estimated_cost <= request.max_cost`

and:

`estimated_latency <= request.max_latency_ms`

### 5. No Eligible Provider

If no provider satisfies the request requirements, the router raises:

`No provider satisfies the cost and latency requirement.`

### 6. Cost Ordering

Eligible providers are sorted by estimated cost.

### 7. Generation

The router attempts providers from cheapest to most expensive.

### 8. Provider Failure

If a provider fails during generation, the router logs the failure and continues to the next eligible provider.

### 9. All Providers Fail

If every eligible provider fails during generation, the router raises:

`All eligible providers failed during generation.`

## Routing Flow

Incoming Request
      |
      v
RouteRequest
      |
      v
Evaluate Providers
      |
      +----------------------+
      |                      |
      v                      v
Estimate Cost        Estimate Latency
      |                      |
      +----------+-----------+
                 |
                 v
       Apply Constraints
                 |
                 v
       Eligible Providers
                 |
                 v
       Sort By Cost
                 |
                 v
       Try Cheapest First
                 |
          +------+------+
          |             |
          v             v
       Success       Failure
          |             |
          v             v
     RouteResponse   Try Next
                        |
                        v
                  Final Failure

## API Models

Request and response models are defined in:

`models/schemas.py`

The router works with:

- `RouteRequest`
- `RouteResponse`

The schemas keep API data structured and validated before it reaches the routing logic.

## API Flow

HTTP Request
  |
  v
Request Validation
  |
  v
CostLatencyRouter
  |
  v
Provider Selection
  |
  v
Provider Generation
  |
  v
RouteResponse

## Project Structure

LLM-Cost-Latency-Router/
|
+-- models/
|   +-- __init__.py
|   +-- schemas.py
|
+-- providers/
|   +-- __init__.py
|   +-- base.py
|   +-- mock.py
|   +-- openai.py
|   +-- gemini.py
|
+-- router/
|   +-- __init__.py
|   +-- router.py
|
+-- tests/
|   +-- test_api.py
|   +-- test_router.py
|
+-- .env
+-- .gitignore
+-- requirements.txt
+-- README.md

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | API framework |
| Pydantic | Request/response validation |
| Pytest | Automated testing |
| OpenAI API | LLM provider |
| Gemini API | LLM provider |
| python-dotenv | Environment configuration |
| Uvicorn | ASGI server |
| Git | Version control |
| GitHub | Source-code hosting |

## Installation

### 1. Clone the repository

`git clone <YOUR_GITHUB_REPOSITORY_URL>`

`cd LLM-Cost-Latency-Router`

### 2. Create a virtual environment

Windows:

`python -m venv venv`

Activate:

`venv\Scripts\activate`

macOS/Linux:

`python3 -m venv venv`

Activate:

`source venv/bin/activate`

### 3. Install dependencies

`pip install -r requirements.txt`

## Environment Variables

Create a `.env` file in the project root.

Required provider credentials:

`OPENAI_API_KEY=your_openai_api_key`

`GEMINI_API_KEY=your_gemini_api_key`

Never place real API keys directly inside source code.

Never commit a `.env` file containing real credentials.

## .gitignore

The repository should ignore sensitive and generated files such as:

`.env`

`venv/`

`__pycache__/`

`*.pyc`

`.pytest_cache/`

## Running the Project

Start the FastAPI application using the project's configured application entry point.

For a standard FastAPI/Uvicorn entry point:

`uvicorn main:app --reload`

Use the actual module path if the project's FastAPI application is defined somewhere other than `main.py`.

Once running, FastAPI normally provides:

Swagger UI:

`http://127.0.0.1:8000/docs`

ReDoc:

`http://127.0.0.1:8000/redoc`

## Testing

The project uses pytest.

Run the complete test suite:

`python -m pytest -q`

Current verified result:

`11 passed, 1 warning`

The warning does not represent a failed test.

## Testing Areas

The test suite covers the implemented routing and API behavior, including:

- Provider abstraction
- Provider properties
- Cost estimation
- Latency estimation
- Provider eligibility
- Cost constraints
- Latency constraints
- Provider selection
- Provider fallback
- API behavior
- Request validation
- Response behavior

## Error Handling

The router handles failures during provider evaluation.

If estimation fails for a provider, the router logs the failure and continues evaluating other providers.

If generation fails for an eligible provider, the router logs the failure and attempts the next eligible provider.

This prevents a single provider failure from immediately terminating every routing attempt.

## Logging

The router uses Python's `logging` module.

Debug-level logging records provider evaluation information such as:

- Provider name
- Model
- Estimated cost
- Estimated latency

Warning-level logging records provider failures during:

- Cost/latency estimation
- Response generation

Info-level logging records the selected provider.

## Security

API credentials are loaded through environment variables.

Do not commit:

- OpenAI API keys
- Gemini API keys
- Access tokens
- Passwords
- Private credentials
- Production secrets

If an API key is accidentally exposed, revoke/rotate it immediately and replace it with a new key.

## Design Principles

### Separation of Concerns

The project separates:

- API handling
- Data validation
- Routing
- Provider implementations
- Testing

### Abstraction

The router communicates through `LLMProvider` rather than directly depending on OpenAI or Gemini implementation details.

### Extensibility

A new provider can be added by implementing the same interface.

### Testability

Mock providers allow the routing system to be tested without external API calls.

### Fault Tolerance

Provider generation failures can trigger fallback to another eligible provider.

## Adding a New Provider

To add a new provider:

1. Create a new file inside `providers/`.
2. Import `LLMProvider`.
3. Create a provider class.
4. Implement `name`.
5. Implement `model`.
6. Implement `generate()`.
7. Implement `estimate_cost()`.
8. Implement `estimate_latency()`.
9. Add the provider to the router configuration.
10. Add automated tests.

Conceptually:

providers/
  |
  +-- base.py
  +-- openai.py
  +-- gemini.py
  +-- mock.py
  +-- new_provider.py

The router can then use the new provider without changing the fundamental routing algorithm.

## Example Provider Interface

A provider follows this conceptual structure:

class NewProvider(LLMProvider):

    @property
    def name(self) -> str:
        return "new-provider"

    @property
    def model(self) -> str:
        return "new-model"

    def generate(self, prompt: str) -> str:
        ...

    def estimate_cost(self, prompt: str) -> float:
        ...

    def estimate_latency(self) -> float:
        ...

## Development Workflow

The development workflow is:

Implement
  |
  v
Run Tests
  |
  v
Fix Failures
  |
  v
Run Full Test Suite
  |
  v
Review Changes
  |
  v
Commit
  |
  v
Push to GitHub

Useful commands:

`python -m pytest -q`

`git status`

`git diff`

`git diff --check`

`git add .`

`git commit -m "Complete LLM cost latency router"`

`git push origin main`

## Future Improvements

Potential improvements include:

- Real provider pricing calculation
- Real-time latency measurement
- Provider health checks
- Dynamic provider availability
- Configurable routing strategies
- Weighted cost/latency scoring
- Automatic retries
- Exponential backoff
- Timeout handling
- Rate-limit handling
- Circuit breakers
- Provider performance analytics
- Usage analytics
- Request tracing
- Prometheus metrics
- Distributed tracing
- Response caching
- Authentication
- API rate limiting
- Docker deployment
- Production monitoring
- Load testing
- Horizontal scaling
- Database-backed usage tracking

## Advanced Routing Strategy

The current router uses estimated cost to order eligible providers.

The architecture can later support a weighted routing score.

For example:

Routing Score =
cost_weight × normalized_cost
+
latency_weight × normalized_latency

A cost-sensitive application could assign greater weight to cost.

A latency-sensitive application could assign greater weight to latency.

The provider abstraction makes this extension possible without changing the provider implementations.

## Engineering Concepts Demonstrated

This project demonstrates practical experience with:

- Python
- Object-oriented programming
- Abstract base classes
- Interface-based design
- Backend architecture
- FastAPI
- Pydantic
- LLM API integration
- Multi-provider architecture
- Cost-aware routing
- Latency-aware routing
- Provider fallback
- Error handling
- Logging
- Automated testing
- Mock providers
- Environment configuration
- Git
- GitHub
- Modular system design

## What I Learned

Through this project, I worked with:

- Designing provider abstractions
- Integrating multiple LLM APIs
- Building backend APIs with FastAPI
- Separating routing logic from provider implementations
- Designing cost and latency constraints
- Implementing fallback behavior
- Writing automated tests
- Using mock providers for deterministic testing
- Handling provider failures
- Managing API credentials through environment variables
- Structuring a modular Python project

## Why This Project

LLM applications often depend on external model providers.

Directly coupling application code to one provider makes it harder to change providers, compare models, implement fallback behavior, or introduce routing policies.

This project separates the application from provider-specific implementation through a common abstraction and centralized routing layer.

The result is a backend architecture that can evolve toward more advanced LLM infrastructure.

## Current Project Status

Core implementation is complete.

Completed:

- Provider abstraction
- OpenAI provider
- Gemini provider
- Mock provider
- Cheap mock provider
- Cost estimation
- Latency estimation
- Cost constraints
- Latency constraints
- Provider selection
- Provider fallback
- Request/response schemas
- API layer
- Automated tests
- Environment-based configuration
- Logging
- GitHub repository

Current verified test result:

`11 passed, 1 warning`

## Resume Project Description

LLM Cost & Latency Router — Built a modular FastAPI-based LLM routing service with OpenAI, Gemini, and mock providers; implemented cost and latency constraint filtering, cost-based provider selection, generation fallback, structured request/response schemas, logging, and automated pytest coverage.

## GitHub Repository Description

LLM routing service with cost and latency-aware provider selection, OpenAI and Gemini integrations, provider fallback, FastAPI APIs, and automated testing.

## Portfolio Highlights

This project demonstrates:

- AI/LLM integration
- Backend engineering
- API development
- Provider abstraction
- Cost-aware infrastructure
- Latency-aware infrastructure
- Fault-tolerant provider selection
- Automated testing
- Modular architecture

## Author

Amrutha BM

BCA | Software Engineering | Backend Development | AI/LLM Systems


## License

This project is intended for learning, experimentation, and portfolio demonstration.

An appropriate open-source license can be added if the repository is later distributed as open-source software.

## Final Architecture Summary

Application
    |
    v
FastAPI
    |
    v
RouteRequest
    |
    v
CostLatencyRouter
    |
    +----------------+----------------+
    |                |                |
    v                v                v
OpenAI           Gemini             Mock
Provider         Provider          Providers
    |                |                |
    v                v                v
OpenAI API       Gemini API       Local Tests
    |
    v
RouteResponse

The project provides a foundation for intelligent LLM provider routing while keeping provider-specific integrations isolated, testable, and replaceable.