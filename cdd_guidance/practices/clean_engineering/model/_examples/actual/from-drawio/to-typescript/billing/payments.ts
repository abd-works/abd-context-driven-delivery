class Payment {
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
  }
  recordFailed(): Payment | PaymentErrors {
  }
}

class PaymentErrors {
  load: string | null;
  unverified: string | null;

  constructor(load: string | null, unverified: string | null) {
    this.load = load;
    this.unverified = unverified;
  }

}

class PaymentCharge {
  title: string;
  submit: string;
  chargedValue: number;

  constructor(title: string, submit: string, chargedValue: number) {
    this.title = title;
    this.submit = submit;
    this.chargedValue = chargedValue;
  }

}

class PaymentIframe {
  html: string;
  transactionId: string;

  constructor(html: string, transactionId: string) {
    this.html = html;
    this.transactionId = transactionId;
  }

}

class FAC {

  constructor() {
  }

  create(customer: Customer): PaymentIframe | Error {
  }
  read(customer: Customer, transactionId: string): PaymentStatus | Error {
  }
}

class PaymentStatus {
  status: string;
  reason: string;

  constructor(status: string, reason: string) {
    this.status = status;
    this.reason = reason;
  }

}

class ApplePayCertificate {
  keyIdentifier: string;
  certificate: string;

  constructor(keyIdentifier: string, certificate: string) {
    this.keyIdentifier = keyIdentifier;
    this.certificate = certificate;
  }

}

class Apple {

  constructor() {
  }

  read(): ApplePayCertificate {
  }
}
