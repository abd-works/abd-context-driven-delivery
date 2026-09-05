declare module 'mongodb' {
  export interface Collection {
    find(filter?: any): { toArray(): Promise<any[]> };
    findOne(filter: any): Promise<any | null>;
    insertOne(doc: any): Promise<any>;
  }
  export interface Db {
    collection(name: string): Collection;
  }
}
