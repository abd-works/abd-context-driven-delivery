router.post('/camp-applications', async (req, res, next) => {
  try { await submit(req); } catch (err) { next(errorCatalogue.fault('CAMP-500', err)); }
});
