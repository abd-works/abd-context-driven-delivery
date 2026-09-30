import { ValidationCode } from '../../../../domain/systems/Cognito/Cognito';

export const enteredValidValidationCode = new ValidationCode('123456');
export const expectedValidValidationCode = enteredValidValidationCode;
export const mismatchValidationCode = new ValidationCode('000000');
export const expiredValidationCode = new ValidationCode('111111');
export const attemptsExceededValidationCode = new ValidationCode('222222');

export const unusableValidationCodeExamples = [
  {
    example: 'mismatch validation code',
    validationCode: mismatchValidationCode,
    helper: "Hmm. That code didn't work.",
  },
  {
    example: 'expired validation code',
    validationCode: expiredValidationCode,
    helper: "Hmm. That code didn't work.",
  },
  {
    example: 'attempts exceeded validation code',
    validationCode: attemptsExceededValidationCode,
    helper: 'Attempts limit exceeded. Please try again later.',
  },
];

export const unusableCognitoValidationCodeExamples = [
  {
    scenario: 'mismatch validation code',
    validationCode: mismatchValidationCode,
    error: 'CodeMismatchException',
  },
  {
    scenario: 'expired validation code',
    validationCode: expiredValidationCode,
    error: 'ExpiredCodeException',
  },
  {
    scenario: 'attempts exceeded validation code',
    validationCode: attemptsExceededValidationCode,
    error: 'LimitExceededException',
  },
];
