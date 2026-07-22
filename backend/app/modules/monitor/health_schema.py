"""Pydantic models representing the expected /health endpoint response format.

These models define what monitored applications should return.
They are used for JSON Schema export and documentation — not for our own API.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field

MetaValue = str | int | float | bool


class HealthComponent(BaseModel):
    """Status of a single component within a monitored application."""

    status: Literal["ok", "degraded", "failed"] = Field(..., description="Component operational status.")
    reason: str | None = Field(None, description="Human-readable explanation, especially for degraded/failed.")
    since: str | None = Field(None, description="ISO 8601 timestamp of when this status began.")
    checked_at: str | None = Field(None, description="ISO 8601 timestamp of the last actual status verification.")
    stale: bool | None = Field(
        None,
        description="True if the reported status may be outdated (e.g. on-demand integrations).",
    )


class HealthResponse(BaseModel):
    """Expected response format for a monitored application's /health endpoint."""

    schema_version: Annotated[int, Field(ge=1)] = Field(
        ...,
        description="Schema version. Currently always 1. Increment on breaking changes.",
    )
    status: Literal["ok", "degraded", "failed"] = Field(
        ...,
        description=("Overall application status. Must reflect the worst status across all components: " "failed > degraded > ok."),
    )
    version: str | None = Field(None, description="Application/release version string.")
    environment: str | None = Field(None, description="Deployment environment (e.g. production, staging).")
    components: dict[str, HealthComponent] | None = Field(None, description="Per-component statuses keyed by component name.")
    last_activity: str | None = Field(
        None,
        description="ISO 8601 timestamp of the last meaningful user/system activity.",
    )
    errors: list[str] | None = Field(
        None,
        description="Active error messages contributing to a degraded/failed status.",
    )
    meta: dict[str, MetaValue] | None = Field(
        None,
        description=("Arbitrary key-value parameters specific to this application " "(e.g. ksef_env, tenant, feature_flags). Values must be scalar."),
    )


def get_health_json_schema() -> dict:
    return HealthResponse.model_json_schema()
