/*
 * Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT.
 */

import * as z from "zod";
import { SmitheryRegistryError } from "./smitheryregistryerror.js";

/**
 * Authentication information is missing or invalid
 */
export type UnauthorizedErrorData = {
  error?: string | undefined;
};

/**
 * Authentication information is missing or invalid
 */
export class UnauthorizedError extends SmitheryRegistryError {
  error?: string | undefined;

  /** The original data that was passed to this error instance. */
  data$: UnauthorizedErrorData;

  constructor(
    err: UnauthorizedErrorData,
    httpMeta: { response: Response; request: Request; body: string },
  ) {
    const message = "message" in err && typeof err.message === "string"
      ? err.message
      : `API error occurred: ${JSON.stringify(err)}`;
    super(message, httpMeta);
    this.data$ = err;
    if (err.error != null) this.error = err.error;

    this.name = "UnauthorizedError";
  }
}

/** @internal */
export const UnauthorizedError$inboundSchema: z.ZodType<
  UnauthorizedError,
  z.ZodTypeDef,
  unknown
> = z.object({
  error: z.string().optional(),
  request$: z.instanceof(Request),
  response$: z.instanceof(Response),
  body$: z.string(),
})
  .transform((v) => {
    return new UnauthorizedError(v, {
      request: v.request$,
      response: v.response$,
      body: v.body$,
    });
  });

/** @internal */
export type UnauthorizedError$Outbound = {
  error?: string | undefined;
};

/** @internal */
export const UnauthorizedError$outboundSchema: z.ZodType<
  UnauthorizedError$Outbound,
  z.ZodTypeDef,
  UnauthorizedError
> = z.instanceof(UnauthorizedError)
  .transform(v => v.data$)
  .pipe(z.object({
    error: z.string().optional(),
  }));

/**
 * @internal
 * @deprecated This namespace will be removed in future versions. Use schemas and types that are exported directly from this module.
 */
export namespace UnauthorizedError$ {
  /** @deprecated use `UnauthorizedError$inboundSchema` instead. */
  export const inboundSchema = UnauthorizedError$inboundSchema;
  /** @deprecated use `UnauthorizedError$outboundSchema` instead. */
  export const outboundSchema = UnauthorizedError$outboundSchema;
  /** @deprecated use `UnauthorizedError$Outbound` instead. */
  export type Outbound = UnauthorizedError$Outbound;
}
