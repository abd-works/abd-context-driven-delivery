/**
 * One required Identity / Address field row (`field`, `requirement`).
 */
class ProfileRequirement {
  field: string;
  requirement: string;

  constructor(field: string, requirement: string) {
    this.field = field;
    this.requirement = requirement;
  }

}

/**
 * Catalog of required Identity / Address rows. Optional preferredName, otherPhoneNumber, complement, city, country are not in this catalog. Persona does not create these rows. `mapInquiry` copies a `# Care` ++PersonaInquiry++ onto the party's Identity / Address; `missing` then lists which catalog rows are still unmet.
 */
class ProfileRequirements {
  // << association >>
  nameRequired: ProfileRequirement;
  // << association >>
  lastNameRequired: ProfileRequirement;
  // << association >>
  dateOfBirthRequired: ProfileRequirement;
  // << association >>
  idNationalityRequired: ProfileRequirement;
  // << association >>
  idTypeRequired: ProfileRequirement;
  // << association >>
  idNumberRequired: ProfileRequirement;
  // << association >>
  expiryRequired: ProfileRequirement;
  // << association >>
  streetRequired: ProfileRequirement;
  // << association >>
  parishRequired: ProfileRequirement;
  // << association >>
  postalCodeRequired: ProfileRequirement;

  constructor(nameRequired: ProfileRequirement, lastNameRequired: ProfileRequirement, dateOfBirthRequired: ProfileRequirement, idNationalityRequired: ProfileRequirement, idTypeRequired: ProfileRequirement, idNumberRequired: ProfileRequirement, expiryRequired: ProfileRequirement, streetRequired: ProfileRequirement, parishRequired: ProfileRequirement, postalCodeRequired: ProfileRequirement) {
    this.nameRequired = nameRequired;
    this.lastNameRequired = lastNameRequired;
    this.dateOfBirthRequired = dateOfBirthRequired;
    this.idNationalityRequired = idNationalityRequired;
    this.idTypeRequired = idTypeRequired;
    this.idNumberRequired = idNumberRequired;
    this.expiryRequired = expiryRequired;
    this.streetRequired = streetRequired;
    this.parishRequired = parishRequired;
    this.postalCodeRequired = postalCodeRequired;
  }

  missing(identity: Identity, address: Address): ProfileRequirement[] {
    // when Identity / Address are updated
    // empty: Confirm ID may proceed
    // otherwise the unmet ProfileRequirement rows
  }
  validateInquiry(identity: Identity): string {
    // Identity.idNumber
    // absent: inquiry required
    // present: already complete
  }
  mapInquiry(customer: Customer, personaInquiry: PersonaInquiry): Customer {
    // maps PersonaInquiry onto Identity / Address
    // expiryDate from PersonaDocument or empty
    // PersonaInquiry.verified from status completed
    // Customer.verified stays false
    // failed inquiry: PersonaInquiry.verified false; Identity / Address may stay empty
  }
  storeFailedInquiry(customer: Customer, personaInquiry: PersonaInquiry): Customer {
    // create failed
    // no field map
    // PersonaInquiry.verified false
    // Customer.verified stays false
  }
}
