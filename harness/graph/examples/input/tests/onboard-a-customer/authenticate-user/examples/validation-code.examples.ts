/** Validation code example data — pass code into ValidationCode at the When step. */

export const emailedValidationCode = { code: '123456' };
export const resentValidationCode = { code: '654321' };
export const resentValidationCodeHelperMessage = 'We sent you a new code. Please check your email.';

export const unusableValidationCodeExamples = [
  { example: 'mismatch validation code', code: '000000', helperMessage: "Hmm. That code didn't work." },
  { example: 'expired validation code', code: '111111', helperMessage: "Hmm. That code didn't work." },
  { example: 'attempts exceeded validation code', code: '222222', helperMessage: 'Attempts limit exceeded. Please try again later.' },
];
