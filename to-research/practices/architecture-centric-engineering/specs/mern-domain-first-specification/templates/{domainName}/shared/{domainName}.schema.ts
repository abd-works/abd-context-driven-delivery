/**
 * {{domainName}}.schema.ts — Zod validation schema for the domain entity.
 *
 * Used at repository boundary (.parse()) and API/form boundary (.safeParse()).
 * Both client/ and server/ import this — single source of truth.
 */
import { z } from 'zod';

export const {{DomainName}}Schema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1, '{{DomainName}} name is required').max(140),
  status: z.enum(['Active', 'Pending', 'Inactive']),
  createdAt: z.coerce.date(),
});

export const Create{{DomainName}}InputSchema = z.object({
  name: z.string().min(1, 'Name is required').max(140),
});

export type Create{{DomainName}}Input = {
  name: string;
};

export type {{DomainName}}DTO = {
  id: string;
  name: string;
  status: 'Active' | 'Pending' | 'Inactive';
  createdAt: Date;
};
