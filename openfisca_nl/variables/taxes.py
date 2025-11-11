"""This file defines variables for the modelled legislation.

A variable is a property of an Entity such as a Person, a Household…

See https://openfisca.org/doc/key-concepts/variables.html
"""

# Import from numpy the what you need to apply on OpenFisca's population vectors
# Import from openfisca-core the objects used to code the legislation in OpenFisca
from numpy import maximum as max_, minimum as min_, where

from openfisca_core.periods import MONTH, YEAR
from openfisca_core.variables import Variable

# Import the Entities specifically defined for this tax and benefit system
from openfisca_nl.entities import Household, Person


class arbeidsinkomen(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Labor income (arbeidsinkomen) for tax purposes"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/werk-en-inkomen/content/wat-is-arbeidsinkomen"

    def formula(person, period, _parameters):
        """Labor income for Dutch tax purposes.
        
        Includes wages, self-employment taxable income, and certain benefits.
        Used to calculate arbeidskorting (labor tax credit).
        """
        # Wages (salary)
        salary = person("salary", period)
        # Self-employment taxable income
        se_income = person("self_employment_taxable_income", period)
        
        # Labor income = salary + self-employment income
        return salary + se_income


class algemene_heffingskorting(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "General tax credit (algemene heffingskorting)"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/heffingskortingen/content/algemene-heffingskorting"

    def formula(person, period, parameters):
        """General tax credit.

        The general tax credit phases out for higher incomes.
        Calculated on an annual basis, then divided by 12 for monthly amount.
        """
        params = parameters(period).taxes.tax_credits
        
        # Annualize monthly taxable income
        monthly_taxable_income = person("taxable_income", period)
        annual_taxable_income = monthly_taxable_income * 12
        
        max_credit = params.algemene_heffingskorting_max
        threshold = params.algemene_heffingskorting_income_threshold
        phase_out_rate = params.algemene_heffingskorting_phase_out_rate
        
        # Phase out above threshold
        excess_income = max_(annual_taxable_income - threshold, 0)
        reduction = excess_income * phase_out_rate
        
        # Annual credit, clamped to 0, then divided by 12 for monthly
        annual_credit = max_(max_credit - reduction, 0)
        return annual_credit / 12


class arbeidskorting(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Labor tax credit (arbeidskorting)"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/heffingskortingen/content/arbeidskorting"

    def formula(person, period, parameters):
        """Labor tax credit.

        The labor tax credit depends on annual labor income (arbeidsinkomen) and phases in and out.
        Calculated on an annual basis, then divided by 12 for monthly amount.
        """
        params = parameters(period).taxes.tax_credits
        
        # Annualize monthly labor income (arbeidsinkomen)
        monthly_arbeidsinkomen = person("arbeidsinkomen", period)
        annual_labor_income = monthly_arbeidsinkomen * 12
        
        max_credit = params.arbeidskorting_max
        max_income = params.arbeidskorting_max_income
        buildup_rate = params.arbeidskorting_buildup_rate
        phase_out_rate = params.arbeidskorting_phase_out_rate
        
        # Build up linearly to max_income
        buildup_credit = annual_labor_income * buildup_rate
        
        # Phase out above max_income
        excess_income = max_(annual_labor_income - max_income, 0)
        phase_out_reduction = excess_income * phase_out_rate
        
        # Credit is min of buildup and max, minus phase-out, clamped to 0
        annual_credit = max_(0, min_(buildup_credit, max_credit) - phase_out_reduction)
        
        # Monthly credit (annual credit divided by 12)
        return annual_credit / 12


class taxable_income(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Total Box 1 taxable income before credits"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/inkomstenbelasting/content/tarieven-inkomstenbelasting"

    def formula(person, period, _parameters):
        """Total Box 1 taxable income.

        Combines base income (salary, capital returns, pension) with
        self-employment income when applicable.
        """
        # Base income = salary + capital_returns + pension
        base_income = (
            person("salary", period)
            + person("capital_returns", period)
            + person("pension", period)
        )
        # Add self-employment taxable income if any
        se_income = person("self_employment_taxable_income", period)
        return base_income + se_income


class income_tax(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Income tax on Box 1 taxable income, after tax credits"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/inkomstenbelasting/content/tarieven-inkomstenbelasting"

    def formula(person, period, parameters):
        """Income tax on Box 1 taxable income, minus tax credits.

        Tax is calculated on taxable income using progressive brackets,
        then tax credits are subtracted.
        
        People at or above AOW age use a different tax scale because they
        do not pay AOW premiums, resulting in a lower effective rate in
        the first bracket.
        """
        taxable_income = person("taxable_income", period)
        
        # Get person's age and AOW age threshold
        age = person("age", period)
        aow_age = parameters(period).general.age_of_retirement
        
        # Select appropriate tax scale based on age
        is_aow_age = age >= aow_age
        scale = parameters(period).taxes.income_tax_brackets_aow
        scale_regular = parameters(period).taxes.income_tax_brackets
        
        # Calculate gross tax using age-appropriate scale
        # Use where() to handle vectorized age comparison
        gross_tax_aow = scale.calc(taxable_income)
        gross_tax_regular = scale_regular.calc(taxable_income)
        gross_tax = where(is_aow_age, gross_tax_aow, gross_tax_regular)
        
        # Subtract tax credits
        algemene_heffingskorting = person("algemene_heffingskorting", period)
        arbeidskorting = person("arbeidskorting", period)
        
        # Tax cannot be negative
        return max_(gross_tax - algemene_heffingskorting - arbeidskorting, 0)


class social_security_contribution(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Progressive contribution paid on salaries to finance social security"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/werk-en-inkomen/content/hoe-werkt-de-inhouding-van-loonheffing"

    def formula(person, period, parameters):
        """Social security contribution.

        The social_security_contribution is computed according to a marginal scale.
        """
        salary = person("salary", period)
        scale = parameters(period).taxes.social_security_contribution

        return scale.calc(salary)


class housing_tax(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR  # This housing tax is defined for a year.
    label = "Property tax (onroerendezaakbelasting - OZB)"
    reference = "https://www.rijksoverheid.nl/onderwerpen/belastingen-voor-particulieren/onroerendezaakbelasting-ozb"

    def formula(household, period, parameters):
        """Housing tax.

        The housing tax is defined for a year, but depends on the `accommodation_size`
        and `housing_occupancy_status` on the first month of the year. Here period
        is a year. We can get the first month of a year with the following shortcut.
        To build different periods, see
        https://openfisca.org/doc/coding-the-legislation/35_periods.html#calculate-dependencies-for-a-specific-period
        """
        january = period.first_month
        accommodation_size = household("accommodation_size", january)

        tax_params = parameters(period).taxes.housing_tax
        tax_amount = max_(
            accommodation_size * tax_params.rate, tax_params.minimal_amount
        )

        # `housing_occupancy_status` is an Enum variable
        occupancy_status = household("housing_occupancy_status", january)
        HousingOccupancyStatus = (
            occupancy_status.possible_values
        )  # Get the enum associated with the variable
        # To access an enum element, we use the `.` notation.
        tenant = occupancy_status == HousingOccupancyStatus.tenant
        owner = occupancy_status == HousingOccupancyStatus.owner

        # The tax is applied only if the household owns or rents its main residency
        return (owner + tenant) * tax_amount
