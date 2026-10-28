// === Porting ===

class Portability {
  donorOperator: string;
  portNumber: string;
  accountNumber: string | null;
  userType: string;
  accountType: string;
  device: string;
  planSelected: string;
  verified: boolean;

  constructor(donorOperator: string, portNumber: string, accountNumber: string | null, userType: string, accountType: string, device: string, planSelected: string, verified: boolean) {
    this.donorOperator = donorOperator;
    this.portNumber = portNumber;
    this.accountNumber = accountNumber;
    this.userType = userType;
    this.accountType = accountType;
    this.device = device;
    this.planSelected = planSelected;
    this.verified = verified;
  }

  verify(portingSmsCode: PortingSmsCode): Portability | PortingErrors {
    throw new Error("not implemented");
  }

  resendSms(): void {
    throw new Error("not implemented");
  }
}

class TwilioService {
  constructor() {
  }

  start(portNumber: string): void {
    throw new Error("not implemented");
  }

  check(portNumber: string, portingSmsCode: PortingSmsCode): void | Error {
    throw new Error("not implemented");
  }
}

class PortingSmsCode {
  code: string;

  constructor(code: string) {
    this.code = code;
  }
}

class PortingErrors {
  portingSmsCode: string | null;

  constructor(portingSmsCode: string | null) {
    this.portingSmsCode = portingSmsCode;
  }
}
