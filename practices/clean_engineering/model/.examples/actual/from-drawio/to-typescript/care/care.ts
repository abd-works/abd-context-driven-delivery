class Case {
  subject: string;

  constructor(subject: string) {
    this.subject = subject;
  }

}

class CaseRepository {
  // << aggregation >>
  cases: Collection<Case>;
  // << association >>
  zendesk: Zendesk;

  constructor(cases: Collection<Case>, zendesk: Zendesk) {
    this.cases = cases;
    this.zendesk = zendesk;
  }

  open(customer: Customer, subject: string): Case {
  }
}

class Ticket {
  id: string;
  subject: string;
  requesterName: string;
  requesterEmail: string;

  constructor(id: string, subject: string, requesterName: string, requesterEmail: string) {
    this.id = id;
    this.subject = subject;
    this.requesterName = requesterName;
    this.requesterEmail = requesterEmail;
  }

}

class Zendesk {

  constructor() {
  }

  create(customer: Customer, subject: string): Ticket {
  }
}

class PersonaInquiry {
  inquiryId: string;
  status: string;
  verified: boolean;
  email: string;
  nameFirst: string;
  nameLast: string;
  birthdate: string;
  selectedCountryCode: string;
  identificationNumber: string;
  identificationClass: string;
  expiryDate: string;
  addressStreet1: string;
  addressStreet2: string;
  addressCity: string;
  addressSubdivision: string;
  addressPostalCode: string;
  addressCountryCode: string;
  currentGovernmentId: string | null;

  constructor(inquiryId: string, status: string, verified: boolean, email: string, nameFirst: string, nameLast: string, birthdate: string, selectedCountryCode: string, identificationNumber: string, identificationClass: string, expiryDate: string, addressStreet1: string, addressStreet2: string, addressCity: string, addressSubdivision: string, addressPostalCode: string, addressCountryCode: string, currentGovernmentId: string | null) {
    this.inquiryId = inquiryId;
    this.status = status;
    this.verified = verified;
    this.email = email;
    this.nameFirst = nameFirst;
    this.nameLast = nameLast;
    this.birthdate = birthdate;
    this.selectedCountryCode = selectedCountryCode;
    this.identificationNumber = identificationNumber;
    this.identificationClass = identificationClass;
    this.expiryDate = expiryDate;
    this.addressStreet1 = addressStreet1;
    this.addressStreet2 = addressStreet2;
    this.addressCity = addressCity;
    this.addressSubdivision = addressSubdivision;
    this.addressPostalCode = addressPostalCode;
    this.addressCountryCode = addressCountryCode;
    this.currentGovernmentId = currentGovernmentId;
  }

}

class PersonaDocument {
  documentId: string;
  expirationDate: string;
  email: string;

  constructor(documentId: string, expirationDate: string, email: string) {
    this.documentId = documentId;
    this.expirationDate = expirationDate;
    this.email = email;
  }

}

class PersonaService {

  constructor() {
  }

  create(customer: Customer): PersonaInquiry {
  }
  readDocument(documentId: string): PersonaDocument | Error {
  }
}
