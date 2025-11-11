"""This file defines variables for the modelled legislation.

A variable is a property of an Entity such as a Person, a Household…

See https://openfisca.org/doc/key-concepts/variables.html
"""

# Import from openfisca-core the objects used to code the legislation in OpenFisca
from openfisca_core.holders import set_input_divide_by_period
from openfisca_core.periods import MONTH
from openfisca_core.populations import DIVIDE
from openfisca_core.variables import Variable

# Import the Entities specifically defined for this tax and benefit system
from openfisca_nl.entities import Household, Person


# This variable is a pure input: it doesn't have a formula
class salary(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    # Optional attribute. Allows user to declare a salary for a year. OpenFisca
    # will spread the yearly amount over the months contained in the year.
    set_input = set_input_divide_by_period
    label = "Salary (gross monthly wage income)"
    reference = (
        "https://www.belastingdienst.nl/wps/wcm/connect/nl/werk-en-inkomen/content/loon"
    )


# This variable is a pure input: it doesn't have a formula
class capital_returns(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    # Optional attribute. Allows user to declare capital returns for a year.
    # OpenFisca will spread the yearly returns over the months within a year.
    set_input = set_input_divide_by_period
    label = "Capital returns (Box 3 income)"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/box-3/box-3"


class disposable_income(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Actual amount available to the household at the end of the month"
    # Some variables represent quantities used in economic models, and not
    # defined by law. Always give the source of your definitions.
    reference = "https://www.cbs.nl/nl-nl/nieuws/2024/16/besteedbaar-inkomen-huishoudens-met-6-5-procent-gestegen"

    def formula(household, period, _parameters):
        """Disposable income.

        Income after taxes and social security contributions.
        Includes salary, self-employment income, capital returns, and pension.

        Note: This is a modeling definition, not CBS's exact definition.
        This matches what the YAML tests assert.
        """
        # Household's job returns is the sum of all its members' salary.
        salary = household.sum(household.members("salary", period))
        # Self-employment taxable income
        se_income = household.sum(
            household.members("self_employment_taxable_income", period)
        )
        # Household's capital returns is the sum of all its members' capital returns.
        capital_returns = household.sum(household.members("capital_returns", period))
        # Pension income
        pension = household.sum(household.members("pension", period))
        # Income tax is the sum of all household members' income tax.
        income_tax = household.sum(household.members("income_tax", period))
        # Housing tax is a household's payment for housing.
        housing_tax = household("housing_tax", period, [DIVIDE])
        # Social security contribution is the sum of all household members'
        # contribution to the financing of the social security.
        social_security_contribution = household.sum(
            household.members("social_security_contribution", period)
        )

        return (
            salary
            + se_income
            + capital_returns
            + pension
            - income_tax
            - housing_tax
            - social_security_contribution
        )


class omzet(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Freelance revenue"


class kosten(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Deductible business expenses"


class winst_voor_aftrek(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Profit before deductions"

    def formula(person, period, _parameters):
        return person("omzet", period) - person("kosten", period)
