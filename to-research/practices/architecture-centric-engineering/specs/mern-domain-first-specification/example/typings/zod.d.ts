declare module 'zod' {
  export interface ZodType<T = any> {
    parse(data: unknown): T;
    safeParse(data: unknown): { success: true; data: T } | { success: false; error: { issues: { message: string }[] } };
  }
  export interface ZodObject<T = any> extends ZodType<T> {}
  export const z: {
    object(shape: Record<string, any>): ZodObject;
    string(): ZodType<string> & { min(n: number, msg?: string): any; max(n: number): any; uuid(): any };
    enum(values: string[]): ZodType;
    coerce: { date(): ZodType<Date> };
    array(type: ZodType): ZodType;
  };
}
