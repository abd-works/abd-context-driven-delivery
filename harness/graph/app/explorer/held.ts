import type { Dispatch, SetStateAction } from 'react';

// A value React state holds and what sets it, as useState answers them.
export type Held<T> = [T, Dispatch<SetStateAction<T>>];
