import type { NextFunction, Request, Response } from 'express'
import { ZodError } from 'zod'

import { CddNotConnectedError, CddToolError } from '@cdd/cdd-connection'
import { CddRequestError } from '@cdd/cdd-shared'

const BAD_REQUEST = 400
const INTERNAL_ERROR = 500
const BAD_GATEWAY = 502
const SERVICE_UNAVAILABLE = 503

export class HttpException extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'HttpException'
  }
}

const statusOf = (failure: unknown): number => {
  if (failure instanceof HttpException) return failure.status
  if (failure instanceof ZodError || failure instanceof CddRequestError) return BAD_REQUEST
  if (failure instanceof CddNotConnectedError) return SERVICE_UNAVAILABLE
  if (failure instanceof CddToolError) return BAD_GATEWAY
  return INTERNAL_ERROR
}

// The one place a failure becomes a reply, so every route fails the same way and the page shows what went wrong.
export function answerFailure(failure: Error, _request: Request, response: Response, _next: NextFunction): void {
  response.status(statusOf(failure)).json({ error: failure.message })
}
