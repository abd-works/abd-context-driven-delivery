class Billing {
  id: string;
  state: string;
  balance: string;
  defaultPayment: any;
  // << composition >>
  invoices: Invoice[];
  // << composition >>
  transactions: Transaction[];

  constructor(id: string, state: string, balance: string, defaultPayment: any, invoices: Invoice[], transactions: Transaction[]) {
    this.id = id;
    this.state = state;
    this.balance = balance;
    this.defaultPayment = defaultPayment;
    this.invoices = invoices;
    this.transactions = transactions;
  }

  create(customer: Customer): Billing | Error {
  }
  applyCredit(): Billing {
  }
}

class BillingRepository {
  // << aggregation >>
  billings: Collection<Billing>;
  // << association >>
  portalGateway: PortalGateway;

  constructor(billings: Collection<Billing>, portalGateway: PortalGateway) {
    this.billings = billings;
    this.portalGateway = portalGateway;
  }

  find(customer: Customer): Billing | null {
  }
  create(customer: Customer): Billing | Error {
  }
}

class Invoice {
  invoiceId: string;
  billDate: string;
  dueDate: string;
  dueAmount: string;
  status: string;

  constructor(invoiceId: string, billDate: string, dueDate: string, dueAmount: string, status: string) {
    this.invoiceId = invoiceId;
    this.billDate = billDate;
    this.dueDate = dueDate;
    this.dueAmount = dueAmount;
    this.status = status;
  }

}

class Transaction {
  id: string;
  paymentDate: string;
  totalAmount: string;

  constructor(id: string, paymentDate: string, totalAmount: string) {
    this.id = id;
    this.paymentDate = paymentDate;
    this.totalAmount = totalAmount;
  }

}

class MavenirBillingAccount {
  id: string;
  name: string;
  href: string;
  state: string;
  ratingType: string;
  billCycle: string;
  defaultPaymentMethod: any;
  relatedParty: any;
  accountBalance: any;
  // << composition >>
  creditAdjustments: MavenirCreditAdjustment[];

  constructor(id: string, name: string, href: string, state: string, ratingType: string, billCycle: string, defaultPaymentMethod: any, relatedParty: any, accountBalance: any, creditAdjustments: MavenirCreditAdjustment[]) {
    this.id = id;
    this.name = name;
    this.href = href;
    this.state = state;
    this.ratingType = ratingType;
    this.billCycle = billCycle;
    this.defaultPaymentMethod = defaultPaymentMethod;
    this.relatedParty = relatedParty;
    this.accountBalance = accountBalance;
    this.creditAdjustments = creditAdjustments;
  }

}

class MavenirInvoice {
  invoiceId: string;
  billDate: string;
  dueDate: string;
  dueAmount: string;
  status: string;

  constructor(invoiceId: string, billDate: string, dueDate: string, dueAmount: string, status: string) {
    this.invoiceId = invoiceId;
    this.billDate = billDate;
    this.dueDate = dueDate;
    this.dueAmount = dueAmount;
    this.status = status;
  }

}

class ArTransaction {
  id: string;
  status: string;
  totalAmount: string;
  paymentDate: string;

  constructor(id: string, status: string, totalAmount: string, paymentDate: string) {
    this.id = id;
    this.status = status;
    this.totalAmount = totalAmount;
    this.paymentDate = paymentDate;
  }

}

class MavenirCreditAdjustment {
  amount: number;
  unit: string;
  glCode: string;
  transactionType: string;
  transactionSubType: string;
  serviceProviderId: string;
  reason: string;

  constructor(amount: number, unit: string, glCode: string, transactionType: string, transactionSubType: string, serviceProviderId: string, reason: string) {
    this.amount = amount;
    this.unit = unit;
    this.glCode = glCode;
    this.transactionType = transactionType;
    this.transactionSubType = transactionSubType;
    this.serviceProviderId = serviceProviderId;
    this.reason = reason;
  }

}

class PortalGateway {

  constructor() {
  }

  createBilling(mavenirCustomer: MavenirCustomer): MavenirBillingAccount | Error {
  }
  read(mavenirCustomer: MavenirCustomer): MavenirBillingAccount | Error {
  }
  readInvoices(mavenirCustomer: MavenirCustomer): MavenirInvoice[] {
  }
  readTransactions(mavenirCustomer: MavenirCustomer): ArTransaction[] {
  }
  readInvoicePdf(billingAccountId: string, invoiceId: string): void {
  }
  applyCredit(mavenirCustomer: MavenirCustomer, creditAdjustment: MavenirCreditAdjustment): MavenirCreditAdjustment {
  }
}
