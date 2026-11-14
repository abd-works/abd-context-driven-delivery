router.post('/camp-applications', async (req, res) => {
  try { await submit(req); } catch (err) { res.status(500).json({ message: err.message, stack: err.stack }); }
});
