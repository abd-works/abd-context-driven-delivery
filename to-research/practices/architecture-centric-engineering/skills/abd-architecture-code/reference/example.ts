/**
 * example.ts — MERN Recipients module: shared + client tiers merged into one file.
 *
 * Reference example showing what an instantiated (placeholder-bound) module looks
 * like after this skill copies a template package and renames it for a story. The
 * canonical runnable equivalent now lives in the template package itself:
 *   `docs/architecture/templates/<slug>/example/` (sentinel-bound version)
 *   `docs/architecture/templates/<slug>/template/` (parameterized version that
 *      this skill substitutes per `parameters.json` to produce per-feature code).
 *
 * This file is preserved as a reading-only reference of *what filled-in output
 * looks like*, kept for back-compat with earlier guidance that pointed to a
 * legacy spec layout (specs/mern-domain-first-specification/example/packages/recipients/).
 *
 * File layout this merges:
 *   shared/
 *     RecipientStatus.ts
 *     recipient.schema.ts
 *     Recipient.ts
 *     Recipients.ts
 *   client/
 *     RecipientClient.ts
 *     Recipient.api.ts
 *     RecipientsClient.ts
 *     useRecipients.ts
 *     RecipientCardView.tsx
 *     RecipientListView.tsx
 */

import { z } from 'zod';
import React, { useState, useEffect, useCallback } from 'react';

// ─────────────────────────────────────────────────────────────────────────────
// shared/RecipientStatus.ts
// ─────────────────────────────────────────────────────────────────────────────

export type RecipientStatusType = 'Active' | 'Pending' | 'Inactive';

export class RecipientStatus {
  constructor(
    public readonly status: RecipientStatusType,
    public readonly createdAt: Date,
    private readonly countryCode: 'US' | 'MX' | 'CA' = 'US'
  ) {}

  private static readonly MX_PENDING_PERIOD_MS = 30 * 60 * 1000;

  isEligibleForPayment(): boolean {
    return this.status === 'Active';
  }

  isPending(): boolean {
    return this.status === 'Pending';
  }

  get remainingPendingMinutes(): number | null {
    if (this.countryCode !== 'MX' || this.status !== 'Pending') return null;
    const elapsed = Date.now() - this.createdAt.getTime();
    const remaining = Math.max(0, RecipientStatus.MX_PENDING_PERIOD_MS - elapsed);
    return Math.ceil(remaining / 60000);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// shared/recipient.schema.ts
// Zod schema used at repository boundary (.parse()) and API/form boundary (.safeParse()).
// ─────────────────────────────────────────────────────────────────────────────

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

// ─────────────────────────────────────────────────────────────────────────────
// shared/Recipient.ts
// Entity and value objects — zero framework imports.
// ─────────────────────────────────────────────────────────────────────────────

export interface BeneficiaryBank {
  swiftBic: string;
  abaRouting?: string;
  name: string;
  addressLine1: string;
  addressLine2?: string;
  city: string;
  country: string;
}

export interface IntermediateBank {
  swiftBic: string;
  name: string;
}

export class Recipient {
  constructor(
    public readonly id: string,
    public readonly enterpriseId: string,
    public readonly name: string,
    public readonly accountNumber: string,
    public readonly accountNumberFull: string,
    public readonly status: RecipientStatus,
    public readonly beneficiaryBank: BeneficiaryBank,
    public readonly intermediateBank: IntermediateBank | undefined,
    public readonly createdAt: Date,
    public readonly activatedAt: Date | undefined,
  ) {}

  isEligibleForPayment(): boolean {
    return this.status.isEligibleForPayment();
  }

  static fromDto(dto: RecipientDTO): Recipient {
    return new Recipient(
      dto.id,
      dto.enterpriseId,
      dto.name,
      dto.accountNumber,
      dto.accountNumberFull,
      new RecipientStatus(dto.status, dto.createdAt),
      dto.beneficiaryBank,
      dto.intermediateBank,
      dto.createdAt,
      dto.activatedAt,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// shared/Recipients.ts
// Collection class — shared client + server.
// ─────────────────────────────────────────────────────────────────────────────

export class Recipients {
  constructor(private readonly items: Recipient[]) {}

  filterByStatus(status: RecipientStatusType): Recipients {
    return new Recipients(this.items.filter(r => r.status.status === status));
  }

  filterByEnterprise(enterpriseId: string): Recipients {
    return new Recipients(this.items.filter(r => r.enterpriseId === enterpriseId));
  }

  search(query: string): Recipients {
    const lower = query.toLowerCase();
    return new Recipients(
      this.items.filter(
        r =>
          r.name.toLowerCase().includes(lower) ||
          r.beneficiaryBank.name.toLowerCase().includes(lower)
      )
    );
  }

  toArray(): Recipient[] {
    return [...this.items];
  }

  get length(): number {
    return this.items.length;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// client/RecipientClient.ts
// Client-tier Recipient — extends shared entity with presentation behavior.
// ─────────────────────────────────────────────────────────────────────────────

export class RecipientClient extends Recipient {
  constructor(
    id: string,
    enterpriseId: string,
    name: string,
    accountNumber: string,
    accountNumberFull: string,
    status: RecipientStatus,
    beneficiaryBank: BeneficiaryBank,
    intermediateBank: IntermediateBank | undefined,
    createdAt: Date,
    activatedAt: Date | undefined,
  ) {
    super(
      id,
      enterpriseId,
      name,
      accountNumber,
      accountNumberFull,
      status,
      beneficiaryBank,
      intermediateBank,
      createdAt,
      activatedAt,
    );
  }

  static fromRecipient(recipient: Recipient): RecipientClient {
    return new RecipientClient(
      recipient.id,
      recipient.enterpriseId,
      recipient.name,
      recipient.accountNumber,
      recipient.accountNumberFull,
      recipient.status,
      recipient.beneficiaryBank,
      recipient.intermediateBank,
      recipient.createdAt,
      recipient.activatedAt,
    );
  }

  get bankName(): string {
    return this.beneficiaryBank.name;
  }

  cardCssClass(isSelected: boolean): string {
    return `recipient-card${isSelected ? ' selected' : ''}`;
  }

  static key(id: string): string {
    return `recipient-${id}`;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// client/Recipient.api.ts
// Fetch wrapper — one function per server route. Wire format → typed objects via schema.
// ─────────────────────────────────────────────────────────────────────────────

const API_BASE = '/api/recipients';

function hydrateRecipients(raw: unknown[]): RecipientClient[] {
  return raw.map(item => {
    const dto = RecipientSchema.parse(item);
    return RecipientClient.fromRecipient(Recipient.fromDto(dto));
  });
}

/** Type-safe HTTP client for Recipient operations. */
export class RecipientApi {
  static async loadByEnterprise(opts?: { activeOnly?: boolean }): Promise<RecipientClient[]> {
    const params = new URLSearchParams();
    if (opts?.activeOnly) params.set('activeOnly', 'true');
    const response = await fetch(`${API_BASE}?${params}`);
    const data = await response.json();
    return hydrateRecipients(data.recipients);
  }

  static async selectByIds(input: SelectRecipientsInput): Promise<RecipientClient[]> {
    const response = await fetch(`${API_BASE}/select`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    const data = await response.json();
    return hydrateRecipients(data.selected);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// client/RecipientsClient.ts
// Client-tier Recipients — extends shared collection with selection and API orchestration.
// ─────────────────────────────────────────────────────────────────────────────

export class RecipientsClient extends Recipients {
  constructor(
    items: Recipient[],
    private readonly selectedIds: Set<string> = new Set(),
  ) {
    super(items);
  }

  static async load(opts?: { activeOnly?: boolean }): Promise<RecipientsClient> {
    const items = await RecipientApi.loadByEnterprise(opts);
    return new RecipientsClient(items);
  }

  withItems(items: Recipient[]): RecipientsClient {
    return new RecipientsClient(items, this.selectedIds);
  }

  search(query: string): RecipientsClient {
    return this.withItems(super.search(query).toArray());
  }

  displayed(query: string): RecipientClient[] {
    const collection = query ? this.search(query) : this;
    return collection.toPresentation();
  }

  toPresentation(): RecipientClient[] {
    return this.toArray().map(r => RecipientClient.fromRecipient(r));
  }

  toggleSelection(id: string): RecipientsClient {
    const next = new Set(this.selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    return new RecipientsClient(this.toArray(), next);
  }

  isSelected(id: string): boolean {
    return this.selectedIds.has(id);
  }

  selectedCount(): number {
    return this.selectedIds.size;
  }

  getSelectedIds(): string[] {
    return Array.from(this.selectedIds);
  }

  getSelected(): Recipient[] {
    return this.toArray().filter(r => this.selectedIds.has(r.id));
  }

  async confirmSelection(): Promise<Recipient[]> {
    const input: SelectRecipientsInput = { recipientIds: this.getSelectedIds() };
    const validation = SelectRecipientsSchema.safeParse(input);
    if (!validation.success) {
      throw new Error(validation.error.issues[0].message);
    }
    return RecipientApi.selectByIds(input);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// client/useRecipients.ts
// React hook — loads domain entities from the API, exposes search/filter via collection class.
// ─────────────────────────────────────────────────────────────────────────────

export function useRecipients() {
  const [collection, setCollection] = useState<RecipientsClient | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    RecipientsClient.load({ activeOnly: true })
      .then(setCollection)
      .finally(() => setLoading(false));
  }, []);

  const toggleRecipient = useCallback((id: string) => {
    setCollection(prev => (prev ? prev.toggleSelection(id) : null));
  }, []);

  const getSelectedRecipients = useCallback(
    () => collection?.getSelected() ?? [],
    [collection],
  );

  const filterBySearch = useCallback(
    (query: string) => collection?.displayed(query) ?? [],
    [collection],
  );

  return {
    recipients: collection?.toPresentation() ?? [],
    selected: collection?.getSelectedIds() ?? [],
    selectedCount: collection?.selectedCount() ?? 0,
    loading,
    toggleRecipient,
    isSelected: (id: string) => collection?.isSelected(id) ?? false,
    getSelectedRecipients,
    filterBySearch,
    confirmSelection: () => collection?.confirmSelection(),
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// client/RecipientCardView.tsx
// Item view — presentation only; delegates to RecipientClient.
// ─────────────────────────────────────────────────────────────────────────────

interface RecipientCardViewProps {
  recipient: RecipientClient;
  isSelected: boolean;
  onToggle: () => void;
}

export function RecipientCardView({ recipient, isSelected, onToggle }: RecipientCardViewProps) {
  return (
    <div
      className={recipient.cardCssClass(isSelected)}
      data-recipient={recipient.id}
      data-selected={isSelected}
      onClick={onToggle}
    >
      <input type="checkbox" checked={isSelected} onChange={onToggle} />
      <div className="info">
        <h3>{recipient.name}</h3>
        <p className="bank">{recipient.bankName}</p>
        <span className="account">Account: {recipient.accountNumber}</span>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// client/RecipientListView.tsx
// Container view — search input + list of card views; delegates to the hook.
// ─────────────────────────────────────────────────────────────────────────────

export function RecipientListView() {
  const {
    recipients,
    selectedCount,
    loading,
    toggleRecipient,
    isSelected,
    filterBySearch,
    confirmSelection,
  } = useRecipients();
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  const displayed = searchQuery ? filterBySearch(searchQuery) : recipients;

  const handleConfirmSelection = async () => {
    try {
      await confirmSelection?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to confirm selection');
    }
  };

  return (
    <div className="recipient-list-view">
      <header>
        <h1>Select Recipient for Wire Payment</h1>
        <input
          type="search"
          placeholder="Search by name or bank..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
      </header>

      {loading && <p>Loading recipients...</p>}
      {!loading && displayed.length === 0 && <p>No active recipients available</p>}
      {error && <p className="error">{error}</p>}

      <div className="recipient-cards" data-testid="recipient-list">
        {displayed.map(r => (
          <RecipientCardView
            key={r.id}
            recipient={r}
            isSelected={isSelected(r.id)}
            onToggle={() => toggleRecipient(r.id)}
          />
        ))}
      </div>

      <footer>
        <p>{selectedCount} recipient(s) selected</p>
        <button onClick={handleConfirmSelection} disabled={selectedCount === 0}>
          Confirm Selection
        </button>
      </footer>
    </div>
  );
}
