from pydantic import BaseModel, Field


class Customer(BaseModel):
    company_name: str
    industry: str
    company_size: int


class CommercialDetails(BaseModel):
    product: str
    subscription_term_months: int
    contract_value_usd: float


class Stakeholder(BaseModel):
    name: str
    role: str
    responsibility: str


class Deal(BaseModel):
    deal_id: str
    deal_name: str
    deal_stage: str

    customer: Customer
    commercial_details: CommercialDetails

    business_objectives: list[str] = Field(default_factory=list)
    stakeholders: list[Stakeholder] = Field(default_factory=list)
    implementation_requirements: list[str] = Field(default_factory=list)

    expected_go_live_date: str | None = None
    implementation_owner: str | None = None

    sales_notes: list[str] = Field(default_factory=list)