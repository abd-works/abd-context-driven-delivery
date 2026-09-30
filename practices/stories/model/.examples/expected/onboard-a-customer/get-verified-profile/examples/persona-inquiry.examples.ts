import {
  PersonaDocument,
  PersonaInquiryFields,
  PersonaInquiryResult,
  PersonaInquiryStatus,
} from '../../../../domain/systems/persona';
import { expectedValidAddress, expectedValidIdentity } from './profile.examples';

export const completedInquiryId = 'inq_test_abc123456';
export const failedInquiryId = 'inq_test_xyz789012';
export const validDocumentId = 'doc_test_abc123456';

export const validPersonaDocument = new PersonaDocument(validDocumentId, '2030-01-15');

export const completedInquiryFields = new PersonaInquiryFields(
  expectedValidIdentity.name,
  expectedValidIdentity.lastName,
  expectedValidIdentity.dateOfBirth,
  expectedValidIdentity.idNationality,
  expectedValidIdentity.idNumber,
  expectedValidIdentity.idType,
  expectedValidIdentity.expiryDate,
  expectedValidAddress.street,
  expectedValidAddress.complement,
  expectedValidAddress.city,
  expectedValidAddress.parish,
  expectedValidAddress.postalCode,
  expectedValidAddress.country,
  validDocumentId,
);

export const completedPersonaInquiryResult = new PersonaInquiryResult(
  completedInquiryId,
  PersonaInquiryStatus.Completed,
  completedInquiryFields,
);

export const failedPersonaInquiryResult = new PersonaInquiryResult(
  failedInquiryId,
  PersonaInquiryStatus.Failed,
  new PersonaInquiryFields(),
);

export const completedInquiryWithoutDocument = new PersonaInquiryResult(
  completedInquiryId,
  PersonaInquiryStatus.Completed,
  new PersonaInquiryFields(
    expectedValidIdentity.name,
    expectedValidIdentity.lastName,
    expectedValidIdentity.dateOfBirth,
    expectedValidIdentity.idNationality,
    expectedValidIdentity.idNumber,
    expectedValidIdentity.idType,
    expectedValidIdentity.expiryDate,
    expectedValidAddress.street,
    expectedValidAddress.complement,
    expectedValidAddress.city,
    expectedValidAddress.parish,
    expectedValidAddress.postalCode,
    expectedValidAddress.country,
    null,
  ),
);
