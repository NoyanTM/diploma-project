from enum import Enum
from typing import Annotated
from datetime import date, datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    field_serializer,
    BeforeValidator,
    PlainSerializer,
)


class LanguageTypeMain(Enum):
    ENGLISH = 1
    KAZAKH = 2
    RUSSIAN = 3


language_dict = {
    LanguageTypeMain.ENGLISH: "en",
    LanguageTypeMain.KAZAKH: "kz",
    LanguageTypeMain.RUSSIAN: "ru",
}


class LanguageTypePublic(str, Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    KAZAKH = "kk"


class Status(str, Enum):
    active = "active"
    former = "former"
    liquidated = "liquidated"
    struck_off = "struck off"
    suspended = "suspended"
    revoked = "revoked"
    dissolved = "dissolved"
    withdrawn = "withdrawn"
    expired = "expired"
    withdrawn_by_participant = "withdrawn by participant"


# class Currency(str, Enum):
#     USD = "USD"
#     RUB = "RUB"
#     KZT = "KZT"
#     EUR = "EUR"










def validate_date(value): # value : str
    # также переделать вызов ошибки и isinstance проверить
    # если подходит по формату то сразу превращать в date, если нет то пихать по for loop ???
    date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"]
    if value == "":
        return None
    if isinstance(value, date): # elif
        return value
    if isinstance(value, str): # elif
        for format in date_formats:
            try:
                return datetime.strptime(value, format).date()
            except ValueError as e:
                pass # print(e)
            # else:
            #     break
        # return None

        # while value is not isinstance(value, date):
        #     try:
        #         for format in date_formats:
        #             return datetime.strptime(value, format).date()
        #     except ValueError as e:
        #         continue # pass
        #     else:
        #         break
        # try:
        #     for format in date_formats:
        #         return datetime.strptime(value, format).date()
        # except ValueError as e:
            # pass
        # try:
        #     for format in date_formats:
        #         return datetime.strptime(value, format).date()
        # except ValueError as e:
        #     print(e) # raise ValueError(e)
    raise ValueError


# def serialize_date(value: date):
#     try:
#         return value.strftime("%d-%m-%Y")
#     except ValueError as e:
#         print(e) # pass
#     # raise ValueError(e)

CustomDate = Annotated[date | None, BeforeValidator(validate_date)] # PlainSerializer(serialize_date)]
CustomDecimal = Annotated[Decimal, Field(ge=0.00, decimal_places=2)] # def validate_decimal, serialize_decimal

    

class OrganizationLicenseIndividual(BaseModel):
    name: str | None = None
    role: str | None = None
    status: Status | None = None
    effective_date: CustomDate | None = None
    expiration_date: CustomDate | None = None


class OrganizationLicense(BaseModel):
    subject_regulation: str | None = None
    license_number: str | None = None
    effective_date: CustomDate | None = None
    expiration_date: CustomDate | None = None
    status: str | None = None
    activities_services: set[str] | None = set()
    description: set[str] | None = set()
    comments: str | None = None
    approved_individuals: list[OrganizationLicenseIndividual] = []


class OrganizationName(BaseModel):
    name: str | None = None
    status: Status | None = None
    effective_date: CustomDate | None = None
    expiration_date: CustomDate | None = None


class OrganizationAddress(BaseModel):
    address: str | None = None
    status: Status | None = None
    effective_date: CustomDate | None = None
    expiration_date: CustomDate | None = None


class OrganizationActivity(BaseModel):
    code: int | None = None
    activity: str | None = None


class OrganizationRole(BaseModel):
    role: str | None = None
    name: str | None = None
    effective_date: CustomDate | None = None
    expiration_date: CustomDate | None = None


class OrganizationShareClasses(BaseModel):
    class_name: str | None = None
    number_shares: CustomDecimal | None = None
    currency: str | None = None # Currency
    price_per_share: CustomDecimal | None = None
    total_cost: CustomDecimal | None = None
    summary_total: CustomDecimal | None = None


class OrganizationCollateralInformation(BaseModel):
    under_collateral: str | None
    additional_information: str | None


class OrganizationShareholders(BaseModel):
    name: str | None = None
    comments: str | None = None
    status: Status | None = None


class Organization(BaseModel):
    bin: Annotated[str, Field(min_length=12, max_length=12)] | None = None
    business_nature: str | None = None
    organisational_legal_form: str | None = None
    registration_date: CustomDate | None = None
    registration_status: Status | None = None
    licenses: list[OrganizationLicense] = []
    names: list[OrganizationName] = []
    addresses: list[OrganizationAddress] = []
    activities: list[OrganizationActivity] = []
    roles: list[OrganizationRole] = []
    share_classes: list[OrganizationShareClasses] = []
    collateral_information: list[OrganizationCollateralInformation] = []
    shareholders: list[OrganizationShareholders] = []


# /roc
# /sps
# /ancillary
# /rnam
# /liquidators
# /authorised_mi
# /authorised
# /dasp
# /fintech
# query params: name, bin_number, form, reg_status, company, license_number, license_status, services, consult_services, products
# 240241900711, 230840900022, 220940900133 - example with single license in "general data"
# 200940900209, 230740900475, 191140900129, 211040900220 - examples with multiple licenses in "general data"
# 240440900327 - example without licenses in "general data"
# 240341900438 - example with empty "capital page"
# 230640900184, 200340900029 - examples with multiple class names in "capital page"
# 230740900198 - пример с поломанным адрессом (когда есть активный но пустой по содержанию адресс)
# нужно собрать примеры со все возможными валютами (240140900346 - KZT, 211140900046 - USD)
# https://publicreg.myafsa.com/licence_details/AFSA-O-LA-2023-0001/ - license data without participants
# https://publicreg.myafsa.com/licence_details/AFSA-G-LA-2023-0006/ - complex activities in license (несколько элементов сразу)
