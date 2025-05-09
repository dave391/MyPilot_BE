from datetime import datetime, timezone
import hashlib


class ZagAuth:
    @staticmethod
    def generate_bearer_token(token_pattern: str) -> str:
        formatted_pattern = ZagAuth.format_token_pattern(token_pattern)
        return ZagAuth.hash_token(formatted_pattern)

    @staticmethod
    def format_token_pattern(token_pattern: str) -> str:
        current_date = datetime.now(timezone.utc)
        return token_pattern.format(
            Year=current_date.year,
            Month=f"{current_date.month:02}",
            Day=f"{current_date.day:02}",
        )

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
