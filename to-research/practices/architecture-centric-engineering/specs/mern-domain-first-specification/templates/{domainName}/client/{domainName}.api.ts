/**
 * {{domainName}}.api.ts — API client (fetch wrapper).
 *
 * Function names match the domain verb exactly.
 * Every function corresponds to a route in {{domainName}}.routes.ts.
 */
import { {{DomainName}} } from '@{{appName}}/{{domainNames}}-shared';

const API_BASE = '/api/{{domainNames}}';

export async function list{{DomainName}}s(
  filters?: { activeOnly?: boolean }
): Promise<{{DomainName}}[]> {
  const params = new URLSearchParams();
  if (filters?.activeOnly) params.set('active_only', 'true');
  const response = await fetch(`${API_BASE}?${params}`);
  return response.json();
}

export async function get{{DomainName}}(id: string): Promise<{{DomainName}}> {
  const response = await fetch(`${API_BASE}/${id}`);
  return response.json();
}

export async function create{{DomainName}}(
  input: Record<string, unknown>
): Promise<{{DomainName}}> {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  return response.json();
}
