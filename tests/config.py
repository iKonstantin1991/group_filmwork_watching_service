from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_url: str = "http://localhost:80"
    token_algorithm: str = "RS256"
    test_private_key: bytes = (
        b"-----BEGIN PRIVATE KEY-----\nMIIBUwIBADANBgkqhkiG9w0BAQEFAASCAT0wggE5AgEAAkEAxU8Phc8K45osm81H\n"
        b"UQmc/4ONf9tlYXWm2i4iSAIJdxHEfH58bdcsbk0pTgSObvtWWBwLpK4HCdp8QsqM\nBvdczQIDAQABAkBdtZzzuk+7pX/GR"
        b"4q1jFFKcZqEvRi7Xvtt6DdT59PC/pGTtAUY\nWCBUoM2aIZrGryrCJ2GYYbehupmN+atMg3iBAiEA607QAIUnF0bwuFVPvD"
        b"OR/Hdu\n2fHNzpfsr1oilnopNj0CIQDWqNL6d3UbQA7/CULFXcp9FazI86RtYiK9dU3B4aC5\n0QIgUjbdMfFT8SwWGzGjh"
        b"Ew4a4+HKZr0n4QxbCr//rd8ArkCIC5X8ny6r6C7esFa\n+Xxs3FuXA1+7IkOvTTrECY6TLMURAiA6HR/oS5GMEBqn2rSUpj"
        b"jpEhb4tYEgv+6l\n0E3Sayq6yQ==\n-----END PRIVATE KEY-----\n"
    )


settings = Settings()  # type: ignore[call-arg]
