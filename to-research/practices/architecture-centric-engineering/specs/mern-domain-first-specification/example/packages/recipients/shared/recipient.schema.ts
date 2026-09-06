import { z } from 'zod';

export const BeneficiaryBankSchema = z.object({
  swiftBic: z.string().regex(/^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$/, 'Invalid SWIFT/BIC'),
  abaRouting: z.string().regex(/^\d{9}$/, 'ABA must be 9 digits').optional(),
  name: z.string().min(1).max(140),
  addressLine1: z.string().min(1).max(70),
  addressLine2: z.string().max(70).optional(),
  city: z.string().min(1).max(35),
  country: z.string().length(2),
});

export const RecipientSchema = z.object({
  id: z.string().uuid(),
  enterpriseId: z.string().uuid(),
  name: z.string().min(1, 'Beneficiary name is required').max(140),
  accountNumber: z.string().min(1),
  accountNumberFull: z.string().min(1),
  status: z.enum(['Active', 'Pending', 'Inactive']),
  beneficiaryBank: BeneficiaryBankSchema,
  intermediateBank: z.object({
    swiftBic: z.string(),
    name: z.string(),
  }).optional(),
  createdAt: z.coerce.date(),
  activatedAt: z.coerce.date().optional(),
});

export type RecipientDTO = z.infer<typeof RecipientSchema>;

export const SelectRecipientsSchema = z.object({
  recipientIds: z.array(z.string().uuid()).min(1, 'Select at least one recipient'),
});

export type SelectRecipientsInput = z.infer<typeof SelectRecipientsSchema>;
