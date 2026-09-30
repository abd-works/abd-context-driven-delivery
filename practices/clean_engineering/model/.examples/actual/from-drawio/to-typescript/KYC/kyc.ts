class ProfileRequirement {
  field: string;
  requirement: string;

  constructor(field: string, requirement: string) {
    this.field = field;
    this.requirement = requirement;
  }

}

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
  }
  validateInquiry(identity: Identity): string {
  }
  mapInquiry(customer: Customer, personaInquiry: PersonaInquiry): Customer {
  }
  storeFailedInquiry(customer: Customer, personaInquiry: PersonaInquiry): Customer {
  }
}
