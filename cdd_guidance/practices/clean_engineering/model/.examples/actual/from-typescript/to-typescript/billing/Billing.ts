class Billing {
  id: string;
  // active | suspended | terminated
  state: string;
  // currentBalance on MavenirBillingAccount.accountBalance
  balance: string;
  // id, status, brand, lastFourDigits
  // Payments token after FAC; account.defaultPaymentMethod
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
    // after Payment approved
    // POST /customer/billing
    // body transactionId ignored
    // 409 when customer.account already present
    // 201 empty body
    PortalGateway.createBilling();
  }
  applyCredit(): Billing {
    // posts onto this account; uses Customer, Cart voucher, and VoucherRedemption already on the graph
    // cook after Vouchera.redeem, before productOrderFromCart
    // skip when VoucherRedemption.success false
    // then appears as Transaction / ArTransaction
    PortalGateway.applyCredit();
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
    // Customer.account[0]
    // assembles invoices, transactions, defaultPayment, balance
    PortalGateway.read();
  }
  create(customer: Customer): Billing | Error {
    PortalGateway.createBilling();
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
  // active | suspended | terminated
  state: string;
  // always POSTPAID
  ratingType: string;
  // always 1st of every month
  billCycle: string;
  defaultPaymentMethod: any;
  relatedParty: any;
  // currentBalance is Paradise Billing.balance
  accountBalance: any;
  // << composition >>
  // posted onto this account
  // PortalGateway.applyCredit
  // then listed as ArTransaction
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
  // always BMD
  unit: string;
  // always 100004
  glCode: string;
  // always creditAdjustment
  transactionType: string;
  // always Credit
  transactionSubType: string;
  // always 100000000
  serviceProviderId: string;
  // always $ + Voucher.campaign
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
    // POST v1/billingAccount?customerId=
    // 409 when account already present
    // 201 no body
  }
  read(mavenirCustomer: MavenirCustomer): MavenirBillingAccount | Error {
    // GET v1/billingAccount/{accountId}
  }
  readInvoices(mavenirCustomer: MavenirCustomer): MavenirInvoice[] {
    // GET v1/invoice/history
  }
  readTransactions(mavenirCustomer: MavenirCustomer): ArTransaction[] {
    // GET allARTransaction
  }
  readInvoicePdf(billingAccountId: string, invoiceId: string): void {
    // GET v1/invoice/invoicePDF
  }
  applyCredit(mavenirCustomer: MavenirCustomer, creditAdjustment: MavenirCreditAdjustment): MavenirCreditAdjustment {
    // POST allARTransaction
    // cook after Vouchera.redeem, before productOrderFromCart
    // skip when VoucherRedemption.success false
  }
}
