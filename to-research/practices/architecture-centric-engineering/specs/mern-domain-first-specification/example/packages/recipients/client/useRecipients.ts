import { useState, useEffect, useCallback } from 'react';
import { RecipientsClient } from './RecipientsClient';

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
