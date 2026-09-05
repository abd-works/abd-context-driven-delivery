import React from 'react';
import { RecipientClient } from './RecipientClient';

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
