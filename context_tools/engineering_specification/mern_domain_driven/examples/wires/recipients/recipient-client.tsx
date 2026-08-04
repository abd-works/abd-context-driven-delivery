import { useEffect, useState } from 'react';
import { Recipient, Recipients, RecipientSchema } from './recipients';

/**
 * recipient-client.tsx — client tier for the recipients domain.
 *
 * HTTP boundary, client domain subclasses, React hook, and views — one file.
 * Must be `.tsx` because it contains JSX. Browser-only; never imported from
 * recipient-server.ts (maintain-layer-purity).
 */

function hydrateRecipients(raw: unknown[]): RecipientClient[] {
  return raw.map((json) => new RecipientClient(RecipientSchema.parse(json)));
}

export class RecipientHttpClient {
  static async loadByEnterprise(opts?: {
    activeOnly?: boolean;
  }): Promise<RecipientClient[]> {
    const params = new URLSearchParams();
    if (opts?.activeOnly) params.set('activeOnly', 'true');
    const response = await fetch(`/api/recipients?${params}`);
    const data = await response.json();
    return hydrateRecipients(data.recipients);
  }
}

export class RecipientClient extends Recipient {
  cardCssClass(isSelected: boolean): string {
    return `recipient-card${isSelected ? ' selected' : ''}`;
  }
}

export class RecipientsClient extends Recipients {
  private constructor(
    items: RecipientClient[],
    private readonly selectedIds: ReadonlySet<string> = new Set(),
  ) {
    super(items);
  }

  static async load(opts?: { activeOnly?: boolean }): Promise<RecipientsClient> {
    const items = await RecipientHttpClient.loadByEnterprise(opts);
    return new RecipientsClient(items);
  }

  toggleSelection(id: string): RecipientsClient {
    const next = new Set(this.selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    return new RecipientsClient(this.toPresentation(), next);
  }

  isSelected(id: string): boolean {
    return this.selectedIds.has(id);
  }

  selectedCount(): number {
    return this.selectedIds.size;
  }

  toPresentation(): RecipientClient[] {
    return this.toArray() as RecipientClient[];
  }
}

export function useRecipients() {
  const [collection, setCollection] = useState<RecipientsClient | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    RecipientsClient.load({ activeOnly: true })
      .then(setCollection)
      .finally(() => setLoading(false));
  }, []);

  return {
    recipients: collection?.toPresentation() ?? [],
    loading,
    toggleRecipient: (id: string) =>
      setCollection((prev) => prev?.toggleSelection(id) ?? prev),
    isSelected: (id: string) => collection?.isSelected(id) ?? false,
    selectedCount: collection?.selectedCount() ?? 0,
  };
}

interface RecipientCardViewProps {
  recipient: RecipientClient;
  isSelected: boolean;
  onToggle: () => void;
}

export function RecipientCardView({
  recipient,
  isSelected,
  onToggle,
}: RecipientCardViewProps) {
  return (
    <div className={recipient.cardCssClass(isSelected)} onClick={onToggle}>
      <h3>{recipient.name}</h3>
      <p className="bank">{recipient.bankName}</p>
    </div>
  );
}

export function RecipientListView() {
  const { recipients, selectedCount, loading, toggleRecipient, isSelected } =
    useRecipients();

  return (
    <div className="recipient-list-view">
      <h1>Select Recipient for Wire Payment</h1>
      {loading && <p>Loading recipients...</p>}
      <div className="recipient-cards" data-testid="recipient-list">
        {recipients.map((r) => (
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
      </footer>
    </div>
  );
}
