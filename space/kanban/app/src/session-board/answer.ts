import type { NextFunction, Request, RequestHandler, Response } from 'express'

// Each object serializes through toJSON(), and a failure goes to the one error handler.
export const answer =
  (work: (req: Request) => unknown): RequestHandler =>
  (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve()
      .then(() => work(req))
      .then(result => res.json(result), next)
  }
