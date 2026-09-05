import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { HomeView } from './HomeView';
import { {{EpicName}}View } from './{{EpicName}}View';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeView />} />
      <Route path="/{{epicSlug}}" element={<{{EpicName}}View />} />
    </Routes>
  );
}
