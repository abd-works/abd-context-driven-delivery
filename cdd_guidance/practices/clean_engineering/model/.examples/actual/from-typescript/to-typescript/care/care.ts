class Case {
  // GWT seven: ID Verification Required | SIM Delivery Required | ID Verification Required and SIM Delivery Required | Promotional trial | Portability Required | Payment failed | Roaming plan - New Subscription
  // cardAdditionFailed config out of GWT
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
    // Create Order Ticket
    // requesterName Identity.fullName
    // requesterEmail Identity.email
    Zendesk.create();
  }
}

class Ticket {
  id: string;
  subject: string;
  // Identity.fullName
  requesterName: string;
  // Identity.email
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
    // always POST tickets.json
    // seven GWT subjects
    // trial may also create id / pSim / idAndPsim
    // cardAdditionFailed config out of GWT
    // requesterName Identity.fullName
    // requesterEmail Identity.email
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
    // wraps a Persona inquiry with inquiryId + status + fields
    // email pre-filled from Customer.identity.email
    // create failed: status failed, verified false
    // Verify Later: create is not called
  }
  readDocument(documentId: string): PersonaDocument | Error {
    // missing document: not found
    // email mismatch: unauthorized
  }
}
