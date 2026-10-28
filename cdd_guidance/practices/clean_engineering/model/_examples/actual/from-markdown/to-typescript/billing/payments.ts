class Payment {
  // always compared to GrowthBook PAYMENT_ATTEMPTS
  // always null until enter
  // always html + transactionId after GET /customer/payment/auth
  paymentAttempts: number;
  // << composition >>
  paymentCharge: PaymentCharge;
  // << composition >>
  paymentErrors: PaymentErrors;

  constructor(paymentAttempts: number, paymentCharge: PaymentCharge, paymentErrors: PaymentErrors) {
    this.paymentAttempts = paymentAttempts;
    this.paymentCharge = paymentCharge;
    this.paymentErrors = paymentErrors;
  }

  enter(cart: Cart): Payment | PaymentErrors {
    // always GET /customer/payment/auth (Authorize Card)
    // always sets Payment.paymentIframe from html + transactionId
    // when PAY_UP_FRONT is off: invoicePayment title Time to add your payment; submit Checkout
    // when PAY_UP_FRONT is on: upfrontPayment title Complete your payment; submit Pay $N and subscribe
    // chargedValue is always Plan.price minus Cart.voucher discount; floor always 0
    // when flag on and no portability.portNumber and not trial voucher and chargedValue > 0: heads-up charged upfront
    // when flag on and chargedValue <= 0 and voucher discount >= 0: heads-up add credit
    // when load fails: PaymentErrors.load
    // PAYMENT_ATTEMPTS is always 3 on the scenario; live default is always 1
    GrowthBook.evaluate();
    GrowthBook.value();
    FAC.create();
  }
  recordFailed(): Payment | PaymentErrors {
    // always POST /customer/payment/failed with transactionId
    // always Then Cart.createOrder
  }
}

/**
 * Commit failures after `Payment.enter` / `Cart.checkout` (card). Billing-account create is `# Billing` on the Customer.
 */
class PaymentErrors {
  // always Failed to load — It's not you, it's me. Please refresh the page.
  load: string | null;
  // always We are unable to verify your card at this time.
  // when attempts under PAYMENT_ATTEMPTS
  unverified: string | null;

  constructor(load: string | null, unverified: string | null) {
    this.load = load;
    this.unverified = unverified;
  }

}

/**
 * Invoice vs upfront copy plus charged amount. From GrowthBook `PAY_UP_FRONT` plus Cart.bundle, Cart.portability, and Cart.voucher.
 */
class PaymentCharge {
  // when invoicePayment: Time to add your payment
  // when upfrontPayment: Complete your payment
  title: string;
  // when invoicePayment: Checkout
  // when upfrontPayment: Pay $N and subscribe
  submit: string;
  // always Plan.price minus Cart.voucher discount; floor always 0
  // table submit Pay $55 is leftover copy
  // FAC SPI auth TotalAmount $1 is FAC.create, not this chargedValue
  chargedValue: number;

  constructor(title: string, submit: string, chargedValue: number) {
    this.title = title;
    this.submit = submit;
    this.chargedValue = chargedValue;
  }

}

/**
 * Wrap target. FAC hosted payment page. No Paradise types.
 */
class PaymentIframe {
  html: string;
  transactionId: string;

  constructor(html: string, transactionId: string) {
    this.html = html;
    this.transactionId = transactionId;
  }

}

/**
 * FAC CCS builds the ++PaymentIframe++. Midtier maps; it is not a type. POST `fac/cards/spi/auth`; GET `getTokenizedCard`.
 */
class FAC {

  constructor() {
  }

  create(customer: Customer): PaymentIframe | Error {
    // Request Payment Authorization
    // Authorize Card (Mavenir)
    // always GET /customer/payment/auth
    // always POST fac/cards/spi/auth
    // stubAuth fixture: transactionId, TotalAmount 1, ON-BOARDING
    // returns html + transactionId
    // FAC timeout 3s no TransactionId: Error 504
  }
  read(customer: Customer, transactionId: string): PaymentStatus | Error {
    // Read Tokenized Card Midtier + Mavenir
    // always GET /customer/payment/status/:transactionId
    // always GET getTokenizedCard
    // completed: status completed, reason APPROVED
    // failed: status failed, reason DECLINED; Midtier 504
    // optional 15s poll is Midtier retry, not a type
  }
}

/**
 * Outcome of a tokenized-card read. No Paradise types. No repository.
 */
class PaymentStatus {
  // completed | failed
  status: string;
  // APPROVED | DECLINED
  reason: string;

  constructor(status: string, reason: string) {
    this.status = status;
    this.reason = reason;
  }

}

/**
 * Wrap target. Apple / DigiCert BM domain certificate Midtier serves. No Paradise types.
 */
class ApplePayCertificate {
  // bmApplePayCert serial CertificateSerialNumber=08b3a3b7b23c2c56a625e95211699f0b
  // live JSON wraps serial in []
  keyIdentifier: string;
  // always certificates.bm whitespace stripped
  certificate: string;

  constructor(keyIdentifier: string, certificate: string) {
    this.keyIdentifier = keyIdentifier;
    this.certificate = certificate;
  }

}

/**
 * Midtier serves the ++ApplePayCertificate++. Apple / DigiCert builds it; Midtier is not a type. POST `/apple/cert` `getCert`.
 */
class Apple {

  constructor() {
  }

  read(): ApplePayCertificate {
    // Provide Apple Pay Certificate
    // always POST /apple/cert getCert
    // always certificates.bm
    // Given CognitoUser vs live unauthenticated /apple
  }
}
