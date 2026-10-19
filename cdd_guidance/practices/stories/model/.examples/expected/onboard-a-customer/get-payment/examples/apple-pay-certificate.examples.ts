import { ApplePayCertificate } from '../../../../domain/billing/Payment';
import { AppleCert } from '../../../../domain/systems/apple';

export const bermudaApplePayCert = new AppleCert(
  '[CertificateSerialNumber=08b3a3b7b23c2c56a625e95211699f0b]',
  'STUB_BM_CERT',
);

export const bermudaApplePayCertificate = new ApplePayCertificate(
  bermudaApplePayCert['key-identifier'],
  bermudaApplePayCert.certificate,
);
