
import random
import string
from typing import Any, Dict

from faker import Faker

from src.models.user import Address, Company, Geo, User

fake = Faker()
Faker.seed(None)


def random_suffix(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_user(**overrides: Any) -> User:
    first, last = fake.first_name(), fake.last_name()
    user = User(
        name=f"{first} {last}",
        username=f"{first.lower()}_{random_suffix()}",
        email=f"{first.lower()}.{last.lower()}.{random_suffix()}@example.com",
        phone=fake.numerify("1-###-###-#### x#####"),
        website=fake.domain_name(),
        address=Address(
            street=fake.street_name(),
            suite=f"Apt. {random.randint(1, 999)}",
            city=fake.city(),
            zipcode=fake.numerify("#####-####"),
            geo=Geo(lat=f"{fake.latitude():.4f}", lng=f"{fake.longitude():.4f}"),
        ),
        company=Company(
            name=fake.company(),
            catchPhrase=fake.catch_phrase(),
            bs=fake.bs(),
        ),
    )
    for key, value in overrides.items():
        setattr(user, key, value)
    return user


def generate_user_payload(**overrides: Any) -> Dict[str, Any]:
    return generate_user(**overrides).to_payload()


def invalid_payloads() -> Dict[str, Dict[str, Any]]:
    return {
        "empty": {},
        "missing_email": {"name": "No Email", "username": "no_email"},
        "blank_name": {"name": "", "username": "blank", "email": "b@example.com"},
        "malformed_email": {"name": "Bad Email", "username": "bad",
                            "email": "not-an-email"},
        "wrong_types": {"name": 12345, "username": True, "email": ["a@b.com"]},
    }
