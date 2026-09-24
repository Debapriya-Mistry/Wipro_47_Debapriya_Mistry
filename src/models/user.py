from __future__ import annotations
from dataclasses import asdict,dataclass,field
from typing import Dict,Any,Optional

@dataclass
class Geo:
    lat:str="0.0000"
    lng:str="0.0000"

@dataclass
class Address:
    street:str="Test Street"
    suite:str="Apt. 1"
    city:str="Test City"
    zipcode:str="12345-6789"
    geo:Geo=field(default_factory=Geo)

@dataclass
class Company:
    name:str="Test Company"
    catchPhrase:str="Automated testing made simple"
    bs:str="quality assurance"

@dataclass
class User:
    name:str
    username:str
    email:str
    phone:str="1-770-736-8031 x56442"
    website:str="example.org"
    address:Address=field(default_factory=Address)
    company:Company=field(default_factory=Company)
    id:Optional[int]=None

    def to_payload(self, include_id: bool = False) -> Dict[str, Any]:
        data = asdict(self)
        if not include_id:
            data.pop("id", None)
        return data

    @classmethod
    def from_response(cls, body: Dict[str, Any]) -> "User":
        address = body.get("address", {}) or {}
        company = body.get("company", {}) or {}
        geo = address.get("geo", {}) or {}
        return cls(
            id=body.get("id"),
            name=body.get("name", ""),
            username=body.get("username", ""),
            email=body.get("email", ""),
            phone=body.get("phone", ""),
            website=body.get("website", ""),
            address=Address(
                street=address.get("street", ""),
                suite=address.get("suite", ""),
                city=address.get("city", ""),
                zipcode=address.get("zipcode", ""),
                geo=Geo(lat=geo.get("lat", ""), lng=geo.get("lng", "")),
            ),
            company=Company(
                name=company.get("name", ""),
                catchPhrase=company.get("catchPhrase", ""),
                bs=company.get("bs", ""),
            ),
        )


