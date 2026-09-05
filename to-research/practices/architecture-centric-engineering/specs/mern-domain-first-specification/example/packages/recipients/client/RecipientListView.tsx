import React, { useState } from 'react';
import { useRecipients } from './useRecipients';
import { RecipientCardView } from './RecipientCardView';

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
