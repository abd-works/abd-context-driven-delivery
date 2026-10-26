export const OnboardingStep = {
  VerifyAccount: 'VerifyAccount',
  SelectPlan: 'SelectPlan',
  PickNumber: 'PickNumber',
  VerifyPortedNumber: 'VerifyPortedNumber',
  SelectSim: 'SelectSim',
  ProfileKyc: 'ProfileKyc',
  Checkout: 'Checkout',
  Done: 'Done',
} as const;

export type OnboardingStep = (typeof OnboardingStep)[keyof typeof OnboardingStep];
