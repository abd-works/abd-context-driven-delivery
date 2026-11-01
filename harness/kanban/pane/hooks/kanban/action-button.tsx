import type { ViewContext } from './view-context'

// Button has no disabled state: an action that is not allowed is drawn dim and does nothing.
export function ActionButtonView({ elements: { Button } }: ViewContext, key: string, label: string, onPress: (() => unknown) | null, isMain = false) {
  return (
    <Button
      key={key}
      label={label}
      dimColor={!onPress}
      variant={isMain && onPress ? 'primary' : 'secondary'}
      onPress={onPress ?? (() => undefined)}
    />
  )
}
