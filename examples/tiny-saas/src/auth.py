"""Password reset for the synthetic tiny-saas example."""

RESET_LINK_TTL_MINUTES = 60


def reset_link_valid(issued_minutes_ago: int) -> bool:
    return 0 <= issued_minutes_ago <= RESET_LINK_TTL_MINUTES
